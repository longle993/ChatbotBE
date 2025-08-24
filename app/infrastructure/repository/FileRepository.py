from core.interface.IFileRepository import IFileRepository
from langchain_core.documents import Document
from typing import List, Dict, Any
from fastapi import UploadFile
from datetime import datetime
import chardet, re, openpyxl, io, base64, os, docx, pandas as pd


class FileRepository(IFileRepository):
    def __init__(self):
        pass

#region Docx
    def convert_file_docx(self, file: UploadFile) -> Document:
        try:
            # Đọc nội dung file vào memory
            file_content = file.file.read()
            
            # Reset file pointer về đầu (nếu cần sử dụng lại)
            file.file.seek(0)
            
            # Tạo BytesIO object từ nội dung file
            docx_stream = io.BytesIO(file_content)
            
            # Đọc file DOCX
            doc = docx.Document(docx_stream)
            
            # Trích xuất text từ tất cả paragraphs
            text_content = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():  # Chỉ thêm paragraph có nội dung
                    text_content.append(paragraph.text.strip())
            
            # Trích xuất text từ tables (nếu có)
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text.strip())
                    if row_text:
                        text_content.append(" | ".join(row_text))
            
            # Kết hợp tất cả text
            full_text = "\n".join(text_content)
            
            # Tạo metadata
            metadata = {
                "filename": file.filename,
                "file_type": "docx",
                "file_size": len(file_content),
                "source": file.filename,
                "page_count": len(doc.paragraphs),  # Số paragraphs như một metric
            }
            
            # Thêm metadata từ document properties (nếu có)
            core_properties = doc.core_properties
            if core_properties.author:
                metadata["author"] = core_properties.author
            if core_properties.title:
                metadata["title"] = core_properties.title
            if core_properties.subject:
                metadata["subject"] = core_properties.subject
            if core_properties.created:
                metadata["created"] = core_properties.created.isoformat()
            if core_properties.modified:
                metadata["modified"] = core_properties.modified.isoformat()
            
            # Tạo và trả về Document
            return Document(
                page_content=full_text,
                metadata=metadata
            )
            
        except Exception as e:
            raise Exception(f"Lỗi khi xử lý file DOCX: {str(e)}")
#endregion

#region Excel
    def combine_text_columns(self, row, headers) -> str:
        return " ".join(f"{header}: {row[header]}" for header in headers if header in row and pd.notna(row[header]))

    def convert_file_xlsx(self, file: UploadFile) -> List[Document]:
        try:
            # Đọc nội dung file
            file_content = file.file.read()
            file.file.seek(0)  # Reset pointer
            
            # Đọc file Excel
            df = pd.read_excel(io.BytesIO(file_content))
            
            # Lấy thông tin cơ bản
            headers = df.columns.tolist()
            total_rows = len(df)
            
            # Lấy metadata từ Excel workbook
            workbook_metadata = {}
            try:
                # Sử dụng openpyxl để lấy metadata chi tiết
                wb = openpyxl.load_workbook(io.BytesIO(file_content), read_only=True)
                props = wb.properties
                
                if props.creator:
                    workbook_metadata["creator"] = props.creator
                if props.title:
                    workbook_metadata["title"] = props.title
                if props.subject:
                    workbook_metadata["subject"] = props.subject
                if props.description:
                    workbook_metadata["description"] = props.description
                if props.created:
                    workbook_metadata["created"] = props.created.isoformat()
                if props.modified:
                    workbook_metadata["modified"] = props.modified.isoformat()
                if props.lastModifiedBy:
                    workbook_metadata["last_modified_by"] = props.lastModifiedBy
                
                # Thông tin về sheets
                workbook_metadata["sheet_names"] = wb.sheetnames
                workbook_metadata["active_sheet"] = wb.active.title if wb.active else None
                
                wb.close()
            except Exception as e:
                # Nếu không lấy được metadata từ openpyxl, bỏ qua
                workbook_metadata["metadata_error"] = str(e)
            
            # Tạo documents
            documents = []
            for index, row in df.iterrows():
                # Kết hợp text từ các cột
                content = self.combine_text_columns(row, headers)
                
                # Tạo metadata cho mỗi row
                row_metadata = {
                    "row_index": int(index),
                    "filename": file.filename,
                    "file_type": "xlsx",
                    "source": file.filename,
                    "total_rows": total_rows,
                    "total_columns": len(headers),
                    "column_headers": headers,
                    "file_size": len(file_content),
                }
                
                # Thêm workbook metadata vào mỗi row
                row_metadata.update(workbook_metadata)
                
                # Thêm thống kê về row hiện tại
                non_null_values = sum(1 for header in headers if header in row and pd.notna(row[header]))
                row_metadata["non_null_values"] = non_null_values
                row_metadata["completeness_ratio"] = round(non_null_values / len(headers), 2)
                
                documents.append(
                    Document(
                        page_content=content,
                        metadata=row_metadata
                    )
                )
            
            return documents
            
        except Exception as e:
            raise Exception(f"Lỗi khi xử lý file Excel: {str(e)}")

    def convert_file_xlsx_advanced(self, file: UploadFile, 
                                sheet_name: str = None, 
                                include_empty_rows: bool = False,
                                chunk_size: int = None) -> List[Document]:
        """
        Phiên bản nâng cao với nhiều tùy chọn
        
        Args:
            file (UploadFile): File Excel được upload
            sheet_name (str): Tên sheet cụ thể (None = sheet đầu tiên)
            include_empty_rows (bool): Có bao gồm rows trống không
            chunk_size (int): Gộp nhiều rows thành một document (None = mỗi row một document)
            
        Returns:
            List[Document]: List các Document objects
        """
        try:          
            file_content = file.file.read()
            file.file.seek(0)
            
            # Đọc sheet cụ thể nếu được chỉ định
            if sheet_name:
                df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_name)
            else:
                df = pd.read_excel(io.BytesIO(file_content))
            
            # Lọc empty rows nếu cần
            if not include_empty_rows:
                df = df.dropna(how='all')
            
            headers = df.columns.tolist()
            
            # Lấy metadata workbook
            workbook_metadata = {}
            try:
                wb = openpyxl.load_workbook(io.BytesIO(file_content), read_only=True)
                props = wb.properties
                
                # Thu thập metadata chi tiết
                metadata_fields = {
                    'creator': props.creator,
                    'title': props.title,
                    'subject': props.subject,
                    'description': props.description,
                    'keywords': props.keywords,
                    'category': props.category,
                    'last_modified_by': props.lastModifiedBy,
                    'company': props.company,
                    'manager': props.manager
                }
                
                for key, value in metadata_fields.items():
                    if value:
                        workbook_metadata[key] = value
                
                if props.created:
                    workbook_metadata["created"] = props.created.isoformat()
                if props.modified:
                    workbook_metadata["modified"] = props.modified.isoformat()
                
                workbook_metadata["sheet_names"] = wb.sheetnames
                workbook_metadata["total_sheets"] = len(wb.sheetnames)
                workbook_metadata["active_sheet"] = wb.active.title if wb.active else None
                
                wb.close()
            except Exception:
                pass
            
            documents = []
            
            # Xử lý theo chunk nếu được chỉ định
            if chunk_size and chunk_size > 1:
                # Gộp nhiều rows thành một document
                for i in range(0, len(df), chunk_size):
                    chunk_df = df.iloc[i:i+chunk_size]
                    
                    # Kết hợp content từ nhiều rows
                    chunk_content = []
                    for _, row in chunk_df.iterrows():
                        row_content = self.combine_text_columns(row, headers)
                        if row_content.strip():  # Chỉ thêm nếu có content
                            chunk_content.append(row_content)
                    
                    if chunk_content:  # Chỉ tạo document nếu có content
                        content = "\n".join(chunk_content)
                        
                        chunk_metadata = {
                            "chunk_index": i // chunk_size,
                            "chunk_start_row": i,
                            "chunk_end_row": min(i + chunk_size - 1, len(df) - 1),
                            "rows_in_chunk": len(chunk_content),
                            "filename": file.filename,
                            "file_type": "xlsx",
                            "source": file.filename,
                            "sheet_name": sheet_name or "Sheet1",
                            "total_rows": len(df),
                            "column_headers": headers,
                            "file_size": len(file_content),
                        }
                        
                        chunk_metadata.update(workbook_metadata)
                        
                        documents.append(Document(
                            page_content=content,
                            metadata=chunk_metadata
                        ))
            else:
                # Xử lý từng row một (như phiên bản gốc)
                for index, row in df.iterrows():
                    content = self.combine_text_columns(row, headers)
                    
                    if content.strip() or include_empty_rows:  # Chỉ tạo document nếu có content hoặc cho phép empty rows
                        row_metadata = {
                            "row_index": int(index),
                            "filename": file.filename,
                            "file_type": "xlsx", 
                            "source": file.filename,
                            "sheet_name": sheet_name or "Sheet1",
                            "total_rows": len(df),
                            "column_headers": headers,
                            "file_size": len(file_content),
                        }
                        
                        row_metadata.update(workbook_metadata)
                        
                        # Thống kê row
                        non_null_values = sum(1 for header in headers if header in row and pd.notna(row[header]))
                        row_metadata["non_null_values"] = non_null_values
                        row_metadata["completeness_ratio"] = round(non_null_values / len(headers), 2)
                        
                        documents.append(Document(
                            page_content=content,
                            metadata=row_metadata
                        ))
            
            return documents
            
        except Exception as e:
            raise Exception(f"Lỗi khi xử lý file Excel: {str(e)}")
#endregion

#region CSV
    def detect_csv_delimiter(sample_text: str) -> str:
        """Phát hiện delimiter của CSV file"""
        # Thử các delimiter phổ biến
        delimiters = [',', ';', '\t', '|', ':']
        
        for delimiter in delimiters:
            try:
                # Đếm số cột trong 3 dòng đầu
                lines = sample_text.split('\n')[:3]
                column_counts = []
                
                for line in lines:
                    if line.strip():
                        columns = line.split(delimiter)
                        column_counts.append(len(columns))
                
                # Nếu số cột nhất quán và > 1, có thể là delimiter đúng
                if len(set(column_counts)) == 1 and column_counts[0] > 1:
                    return delimiter
            except:
                continue
        
        return ','  # Default fallback

    def clean_header_names(headers: list) -> list:
        """Làm sạch tên headers"""
        cleaned = []
        for header in headers:
            # Strip whitespace
            clean_header = str(header).strip()
            
            # Xử lý tên cột trống
            if not clean_header or clean_header.lower() in ['unnamed', 'nan']:
                clean_header = f"column_{len(cleaned)}"
            
            # Loại bỏ ký tự đặc biệt có thể gây vấn đề
            clean_header = re.sub(r'[^\w\s-]', '_', clean_header)
            
            cleaned.append(clean_header)
        
        return cleaned

    def combine_csv_row_columns(self, row, headers) -> str:
        parts = []
        for header in headers:
            if header in row and pd.notna(row[header]) and str(row[header]).strip():
                value = str(row[header]).strip()
                parts.append(f"{header}: {value}")
        return " | ".join(parts)

    def convert_file_csv(self, file: UploadFile) -> List[Document]:
        try:
            # Đọc nội dung file
            file_content = file.file.read()
            file.file.seek(0)
            
            # Phát hiện encoding
            detected_encoding = chardet.detect(file_content)
            encoding = detected_encoding.get('encoding', 'utf-8')
            
            # Decode nội dung
            try:
                text_content = file_content.decode(encoding)
            except UnicodeDecodeError:
                # Thử các encoding phổ biến
                for fallback_encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        text_content = file_content.decode(fallback_encoding)
                        encoding = fallback_encoding
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise Exception("Không thể decode file CSV")
            
            # Phát hiện delimiter
            delimiter = self.detect_csv_delimiter(text_content[:1000])  # Sample 1000 ký tự đầu
            
            # Đọc CSV với pandas
            try:
                df = pd.read_csv(
                    io.StringIO(text_content),
                    delimiter=delimiter,
                    encoding=None,  # Đã decode rồi
                    na_values=['', 'NA', 'N/A', 'NULL', 'null', 'None'],
                    keep_default_na=True,
                    skip_blank_lines=True
                )
            except Exception as e:
                # Fallback: thử với delimiter khác
                for fallback_delimiter in [',', ';', '\t']:
                    if fallback_delimiter != delimiter:
                        try:
                            df = pd.read_csv(io.StringIO(text_content), delimiter=fallback_delimiter)
                            delimiter = fallback_delimiter
                            break
                        except:
                            continue
                else:
                    raise Exception(f"Không thể parse CSV: {str(e)}")
            
            # Làm sạch headers
            original_headers = df.columns.tolist()
            clean_headers = self.clean_header_names(original_headers)
            df.columns = clean_headers
            
            # Thống kê CSV
            total_rows = len(df)
            total_columns = len(df.columns)
            non_empty_cells = df.count().sum()  # Tổng số cells không null
            total_cells = total_rows * total_columns
            
            # Phát hiện kiểu dữ liệu của columns
            column_types = {}
            for col in df.columns:
                dtype = str(df[col].dtype)
                non_null_count = df[col].count()
                unique_count = df[col].nunique()
                
                column_types[col] = {
                    "dtype": dtype,
                    "non_null_count": int(non_null_count),
                    "unique_values": int(unique_count),
                    "null_percentage": round((total_rows - non_null_count) / total_rows * 100, 1)
                }
            
            # Metadata chung cho tất cả documents
            base_metadata = {
                "filename": file.filename,
                "file_type": "csv",
                "source": file.filename,
                "file_size": len(file_content),
                "encoding": encoding,
                "delimiter": delimiter,
                "total_rows": total_rows,
                "total_columns": total_columns,
                "column_names": clean_headers,
                "original_headers": original_headers,
                "column_types": column_types,
                "data_completeness": round(non_empty_cells / total_cells * 100, 1),
                "non_empty_cells": int(non_empty_cells),
            }
            
            # Tạo documents cho mỗi row
            documents = []
            for index, row in df.iterrows():
                # Kết hợp content từ các columns
                content = self.combine_csv_row_columns(row, clean_headers)
                
                # Skip empty rows nếu không có content
                if not content.strip():
                    continue
                
                # Metadata cho row này
                row_metadata = base_metadata.copy()
                row_metadata.update({
                    "row_index": int(index),
                    "row_number": int(index + 1),  # 1-indexed cho user-friendly
                })
                
                # Thống kê row hiện tại
                non_null_values = sum(1 for col in clean_headers if col in row and pd.notna(row[col]))
                row_metadata.update({
                    "non_null_values": non_null_values,
                    "completeness_ratio": round(non_null_values / total_columns, 2),
                    "empty_fields": total_columns - non_null_values,
                })
                
                documents.append(
                    Document(
                        page_content=content,
                        metadata=row_metadata
                    )
                )
            
            return documents
            
        except Exception as e:
            raise Exception(f"Lỗi khi xử lý file CSV: {str(e)}")

    def convert_file_csv_advanced(self, file: UploadFile,
                                chunk_rows: int = None,
                                include_headers_in_content: bool = True,
                                custom_na_values: list = None,
                                skip_rows: int = 0,
                                max_rows: int = None) -> List[Document]:
        """
        Phiên bản nâng cao với nhiều tùy chọn
        
        Args:
            file (UploadFile): File CSV được upload
            chunk_rows (int): Số rows mỗi chunk (None = mỗi row một document)
            include_headers_in_content (bool): Bao gồm tên cột trong content
            custom_na_values (list): Danh sách custom NA values
            skip_rows (int): Bỏ qua n dòng đầu
            max_rows (int): Chỉ đọc tối đa n dòng
            
        Returns:
            List[Document]: List các Document objects
        """
        try:
            if not file.filename.lower().endswith('.csv'):
                raise ValueError("File phải có định dạng .csv")
            
            file_content = file.file.read()
            file.file.seek(0)
            
            # Detect encoding
            detected = chardet.detect(file_content)
            encoding = detected.get('encoding', 'utf-8')
            
            try:
                text_content = file_content.decode(encoding)
            except UnicodeDecodeError:
                text_content = file_content.decode('utf-8', errors='replace')
                encoding = 'utf-8 (with replacement)'
            
            # Detect delimiter
            delimiter = self.detect_csv_delimiter(text_content[:1000])
            
            # Custom NA values
            na_values = custom_na_values or ['', 'NA', 'N/A', 'NULL', 'null', 'None', '#N/A', '#NULL!']
            
            # Read CSV with advanced options
            read_params = {
                'delimiter': delimiter,
                'na_values': na_values,
                'keep_default_na': True,
                'skip_blank_lines': True,
                'encoding': None,  # Already decoded
            }
            
            if skip_rows > 0:
                read_params['skiprows'] = skip_rows
            if max_rows:
                read_params['nrows'] = max_rows
            
            try:
                df = pd.read_csv(io.StringIO(text_content), **read_params)
            except Exception as e:
                raise Exception(f"Không thể parse CSV: {str(e)}")
            
            # Clean headers
            clean_headers = self.clean_header_names(df.columns.tolist())
            df.columns = clean_headers
            
            # Base metadata
            base_metadata = {
                "filename": file.filename,
                "file_type": "csv",
                "source": file.filename,
                "file_size": len(file_content),
                "encoding": encoding,
                "delimiter": delimiter,
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "column_names": clean_headers,
                "skipped_rows": skip_rows,
                "max_rows_limit": max_rows,
            }
            
            documents = []
            
            if chunk_rows and chunk_rows > 1:
                # Chunking mode: gộp nhiều rows thành một document
                for i in range(0, len(df), chunk_rows):
                    chunk_df = df.iloc[i:i+chunk_rows]
                    
                    # Combine content từ nhiều rows
                    chunk_contents = []
                    for _, row in chunk_df.iterrows():
                        if include_headers_in_content:
                            row_content = self.combine_csv_row_columns(row, clean_headers)
                        else:
                            row_content = " | ".join([str(val) for val in row.values if pd.notna(val)])
                        
                        if row_content.strip():
                            chunk_contents.append(row_content)
                    
                    if chunk_contents:
                        content = "\n".join(chunk_contents)
                        
                        chunk_metadata = base_metadata.copy()
                        chunk_metadata.update({
                            "chunk_index": i // chunk_rows,
                            "chunk_start_row": i,
                            "chunk_end_row": min(i + chunk_rows - 1, len(df) - 1),
                            "rows_in_chunk": len(chunk_contents),
                            "processing_mode": "chunked",
                        })
                        
                        documents.append(Document(
                            page_content=content,
                            metadata=chunk_metadata
                        ))
            else:
                # Single row mode (mặc định)
                for index, row in df.iterrows():
                    if include_headers_in_content:
                        content = self.combine_csv_row_columns(row, clean_headers)
                    else:
                        content = " | ".join([str(val) for val in row.values if pd.notna(val)])
                    
                    if not content.strip():
                        continue
                    
                    row_metadata = base_metadata.copy()
                    row_metadata.update({
                        "row_index": int(index),
                        "row_number": int(index + 1),
                        "processing_mode": "single_row",
                    })
                    
                    # Row statistics
                    non_null_values = sum(1 for val in row.values if pd.notna(val))
                    row_metadata.update({
                        "non_null_values": non_null_values,
                        "completeness_ratio": round(non_null_values / len(clean_headers), 2),
                    })
                    
                    documents.append(Document(
                        page_content=content,
                        metadata=row_metadata
                    ))
            
            return documents
            
        except Exception as e:
            raise Exception(f"Lỗi khi xử lý file CSV: {str(e)}")

    def analyze_csv_structure(self, file: UploadFile) -> Dict[str, Any]:
        """
        Phân tích cấu trúc của CSV file mà không tạo documents
        
        Args:
            file (UploadFile): File CSV được upload
            
        Returns:
            Dict: Thông tin phân tích về cấu trúc CSV
        """
        try:
            file_content = file.file.read()
            file.file.seek(0)
            
            # Detect encoding
            detected = chardet.detect(file_content)
            encoding = detected.get('encoding', 'utf-8')
            text_content = file_content.decode(encoding, errors='replace')
            
            # Detect delimiter
            delimiter = self.detect_csv_delimiter(text_content[:1000])
            
            # Quick analysis with small sample
            df_sample = pd.read_csv(
                io.StringIO(text_content),
                delimiter=delimiter,
                nrows=100  # Only read first 100 rows for analysis
            )
            
            # Clean headers
            clean_headers = self.clean_header_names(df_sample.columns.tolist())
            
            # Column analysis
            column_analysis = {}
            for col in clean_headers:
                if col in df_sample.columns:
                    col_data = df_sample[col]
                    column_analysis[col] = {
                        "dtype": str(col_data.dtype),
                        "non_null_count": int(col_data.count()),
                        "unique_values": int(col_data.nunique()),
                        "null_percentage": round((len(col_data) - col_data.count()) / len(col_data) * 100, 1),
                        "sample_values": col_data.dropna().head(3).tolist(),
                    }
            
            return {
                "filename": file.filename,
                "file_size": len(file_content),
                "encoding": encoding,
                "delimiter": delimiter,
                "estimated_total_rows": text_content.count('\n'),
                "columns_count": len(clean_headers),
                "column_names": clean_headers,
                "column_analysis": column_analysis,
                "sample_rows": min(100, len(df_sample)),
            }
            
        except Exception as e:
            return {"error": f"Lỗi khi phân tích CSV: {str(e)}"}
#endregion

#region Text
    def convert_file_txt(self, file: UploadFile) -> Document:

        try:
            # Đọc nội dung file dưới dạng bytes
            file_content = file.file.read()
            
            # Reset file pointer
            file.file.seek(0)
            
            # Phát hiện encoding
            detected_encoding = chardet.detect(file_content)
            encoding = detected_encoding.get('encoding', 'utf-8')
            confidence = detected_encoding.get('confidence', 0.0)
            
            # Thử decode với encoding được phát hiện
            try:
                text_content = file_content.decode(encoding)
            except UnicodeDecodeError:
                # Fallback encoding nếu decode thất bại
                fallback_encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252', 'ascii']
                text_content = None
                used_encoding = None
                
                for fallback_encoding in fallback_encodings:
                    try:
                        text_content = file_content.decode(fallback_encoding)
                        used_encoding = fallback_encoding
                        break
                    except UnicodeDecodeError:
                        continue
                
                if text_content is None:
                    raise Exception("Không thể decode file với bất kỳ encoding nào")
                
                encoding = used_encoding
                confidence = 0.0  # Đánh dấu là fallback
            
            # Thống kê nội dung
            lines = text_content.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            words = text_content.split()
            
            # Phát hiện định dạng đặc biệt
            file_format = self.detect_text_format(text_content)
            
            # Tạo metadata
            metadata = {
                "filename": file.filename,
                "file_type": "txt",
                "source": file.filename,
                "file_size": len(file_content),
                "encoding": encoding,
                "encoding_confidence": round(confidence, 2),
                "total_lines": len(lines),
                "non_empty_lines": len(non_empty_lines),
                "word_count": len(words),
                "char_count": len(text_content),
                "detected_format": file_format,
            }
            
            # Thêm thống kê chi tiết
            if text_content.strip():
                # Độ dài trung bình của dòng
                avg_line_length = sum(len(line) for line in non_empty_lines) / len(non_empty_lines) if non_empty_lines else 0
                metadata["avg_line_length"] = round(avg_line_length, 1)
                
                # Độ dài trung bình của từ
                avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
                metadata["avg_word_length"] = round(avg_word_length, 1)
                
                # Phát hiện ngôn ngữ có thể (dựa trên ký tự)
                language_hints = self.detect_language_hints(text_content)
                if language_hints:
                    metadata["language_hints"] = language_hints
            
            # Tạo và trả về Document
            return Document(
                page_content=text_content,
                metadata=metadata
            )
            
        except Exception as e:
            raise Exception(f"Lỗi khi xử lý file TXT: {str(e)}")

    def detect_text_format(text: str) -> str:
        """Phát hiện định dạng đặc biệt của file text"""
        text_lower = text.lower().strip()
        
        # CSV format
        if ',' in text and '\n' in text:
            lines = text.split('\n')[:5]  # Kiểm tra 5 dòng đầu
            comma_counts = [line.count(',') for line in lines if line.strip()]
            if comma_counts and all(count > 0 and count == comma_counts[0] for count in comma_counts):
                return "csv_like"
        
        # JSON format
        if text_lower.startswith('{') and text_lower.endswith('}'):
            return "json_like"
        elif text_lower.startswith('[') and text_lower.endswith(']'):
            return "json_array_like"
        
        # XML/HTML format
        if '<' in text and '>' in text:
            if text_lower.startswith('<?xml') or text_lower.startswith('<!doctype'):
                return "xml_like"
            elif '<html' in text_lower or '<!doctype html' in text_lower:
                return "html_like"
            elif text.count('<') > 5 and text.count('>') > 5:
                return "markup_like"
        
        # Code format
        code_indicators = ['def ', 'function ', 'class ', 'import ', '#include', 'var ', 'const ']
        if any(indicator in text for indicator in code_indicators):
            return "code_like"
        
        # Log format
        if any(pattern in text_lower for pattern in ['error:', 'warning:', 'info:', '[log]', 'timestamp']):
            return "log_like"
        
        # Markdown format
        if any(pattern in text for pattern in ['# ', '## ', '### ', '* ', '- ', '```']):
            return "markdown_like"
        
        # Email format
        if '@' in text and any(pattern in text_lower for pattern in ['from:', 'to:', 'subject:']):
            return "email_like"
        
        return "plain_text"

    def detect_language_hints(text: str) -> list:
        """Phát hiện gợi ý ngôn ngữ dựa trên ký tự"""
        hints = []
        
        # Tiếng Việt
        vietnamese_chars = ['ă', 'â', 'ê', 'ô', 'ơ', 'ư', 'đ', 'á', 'à', 'ả', 'ã', 'ạ']
        if any(char in text.lower() for char in vietnamese_chars):
            hints.append("vietnamese")
        
        # Tiếng Trung
        chinese_range = any('\u4e00' <= char <= '\u9fff' for char in text)
        if chinese_range:
            hints.append("chinese")
        
        # Tiếng Nhật
        japanese_ranges = [
            any('\u3040' <= char <= '\u309f' for char in text),  # Hiragana
            any('\u30a0' <= char <= '\u30ff' for char in text),  # Katakana
        ]
        if any(japanese_ranges):
            hints.append("japanese")
        
        # Tiếng Hàn
        korean_range = any('\uac00' <= char <= '\ud7af' for char in text)
        if korean_range:
            hints.append("korean")
        
        # Tiếng Nga
        russian_range = any('\u0400' <= char <= '\u04ff' for char in text)
        if russian_range:
            hints.append("russian")
        
        # Tiếng Ả Rập
        arabic_range = any('\u0600' <= char <= '\u06ff' for char in text)
        if arabic_range:
            hints.append("arabic")
        
        # Nếu chỉ có ASCII, có thể là tiếng Anh
        if not hints and all(ord(char) < 128 for char in text if char.isalpha()):
            hints.append("english_likely")
        
        return hints

    def convert_file_txt_advanced(self, file: UploadFile, 
                                chunk_by_lines: int = None,
                                chunk_by_chars: int = None,
                                preserve_line_breaks: bool = True) -> list[Document]:
        """
        Phiên bản nâng cao với tính năng chia chunk
        
        Args:
            file (UploadFile): File TXT được upload
            chunk_by_lines (int): Chia chunk theo số dòng (None = không chia)
            chunk_by_chars (int): Chia chunk theo số ký tự (None = không chia)
            preserve_line_breaks (bool): Giữ nguyên line breaks
            
        Returns:
            list[Document]: List các Document objects (có thể là nhiều chunk)
        """
        try:
            if not file.filename.lower().endswith('.txt'):
                raise ValueError("File phải có định dạng .txt")
            
            file_content = file.file.read()
            file.file.seek(0)
            
            # Detect encoding
            detected = chardet.detect(file_content)
            encoding = detected.get('encoding', 'utf-8')
            
            try:
                text_content = file_content.decode(encoding)
            except UnicodeDecodeError:
                text_content = file_content.decode('utf-8', errors='replace')
                encoding = 'utf-8 (with replacement)'
            
            # Base metadata
            base_metadata = {
                "filename": file.filename,
                "file_type": "txt",
                "source": file.filename,
                "file_size": len(file_content),
                "encoding": encoding,
                "total_chars": len(text_content),
            }
            
            # Nếu không chia chunk, trả về document duy nhất
            if not chunk_by_lines and not chunk_by_chars:
                return [self.convert_file_txt(file)]
            
            documents = []
            
            if chunk_by_lines:
                # Chia theo số dòng
                lines = text_content.split('\n')
                for i in range(0, len(lines), chunk_by_lines):
                    chunk_lines = lines[i:i + chunk_by_lines]
                    chunk_content = '\n'.join(chunk_lines) if preserve_line_breaks else ' '.join(chunk_lines)
                    
                    chunk_metadata = base_metadata.copy()
                    chunk_metadata.update({
                        "chunk_index": i // chunk_by_lines,
                        "chunk_type": "by_lines",
                        "chunk_start_line": i,
                        "chunk_end_line": min(i + chunk_by_lines - 1, len(lines) - 1),
                        "lines_in_chunk": len(chunk_lines),
                        "chars_in_chunk": len(chunk_content),
                    })
                    
                    documents.append(Document(
                        page_content=chunk_content,
                        metadata=chunk_metadata
                    ))
            
            elif chunk_by_chars:
                # Chia theo số ký tự
                for i in range(0, len(text_content), chunk_by_chars):
                    chunk_content = text_content[i:i + chunk_by_chars]
                    
                    chunk_metadata = base_metadata.copy()
                    chunk_metadata.update({
                        "chunk_index": i // chunk_by_chars,
                        "chunk_type": "by_chars",
                        "chunk_start_char": i,
                        "chunk_end_char": min(i + chunk_by_chars - 1, len(text_content) - 1),
                        "chars_in_chunk": len(chunk_content),
                    })
                    
                    documents.append(Document(
                        page_content=chunk_content,
                        metadata=chunk_metadata
                    ))
            
            return documents
            
        except Exception as e:
            raise Exception(f"Lỗi khi xử lý file TXT: {str(e)}")

#endregion

    
    def extract_file(self, documents: list[UploadFile]) -> List[Document]:
        list_docs = []
        for doc in documents:
            if doc.filename.endswith(".docx"):
                list_docs.append(self.convert_file_docx(doc))
            elif doc.filename.endswith(".xlsx"):
                list_docs.extend(self.convert_file_xlsx(doc))
            elif doc.filename.endswith(".csv"):
                list_docs.append(self.convert_file_csv(doc))
            elif doc.filename.endswith(".txt"):
                list_docs.append(self.convert_file_txt(doc))

        return list_docs
