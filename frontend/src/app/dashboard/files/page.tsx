"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  CircularProgress,
  Alert,
  Snackbar,
  Chip
} from "@mui/material";
import {
  CloudUpload as CloudUploadIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  InsertDriveFile as FileIcon
} from "@mui/icons-material";
import { fileApi, FileRecord } from "@/lib/api/files";
import { trackEvent } from "@/lib/api/analytics";

export default function FileManagerPage() {
  const [files, setFiles] = useState<FileRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    trackEvent("page_view", { page: "files" });
  }, []);

  const fetchFiles = async () => {
    try {
      setLoading(true);
      const data = await fileApi.getFiles();
      setFiles(data);
    } catch (err: any) {
      setError(err.message || "Failed to load files");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    try {
      setUploading(true);
      await fileApi.uploadFile(selectedFile);
      trackEvent("file_upload", { size: selectedFile.size, type: selectedFile.type });
      setSuccessMsg("File uploaded successfully");
      await fetchFiles();
    } catch (err: any) {
      setError(err.message || "Upload failed");
    } finally {
      setUploading(false);
      // Reset input so that selecting the same file triggers onChange again
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleDelete = async (id: string, filename: string) => {
    if (!confirm(`Are you sure you want to permanently delete '${filename}'?`)) return;
    try {
      await fileApi.deleteFile(id);
      setSuccessMsg("File deleted");
      await fetchFiles();
    } catch (err: any) {
      setError(err.message || "Delete failed");
    }
  };

  const handleDownload = async (id: string, filename: string) => {
    try {
      await fileApi.downloadFile(id, filename);
    } catch (err: any) {
      setError(err.message || "Download failed");
    }
  };

  const formatBytes = (bytes: number, decimals = 2) => {
    if (!+bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
  };
  
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString();
  };

  return (
    <Box sx={{ p: 1 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4 }}>
        <Typography variant="h4" fontWeight="bold">
          Storage Explorer
        </Typography>
        <Box>
           <input
             type="file"
             style={{ display: "none" }}
             ref={fileInputRef}
             onChange={handleFileSelect}
           />
           <Button
             variant="contained"
             color="primary"
             startIcon={uploading ? <CircularProgress size={20} color="inherit" /> : <CloudUploadIcon />}
             onClick={() => fileInputRef.current?.click()}
             disabled={uploading}
             sx={{ borderRadius: 2, px: 3 }}
           >
             {uploading ? "Uploading..." : "Upload File"}
           </Button>
        </Box>
      </Box>

      <Card sx={{ borderRadius: 3, boxShadow: "0 8px 32px rgba(0,0,0,0.04)" }}>
        <CardContent sx={{ p: 0, "&:last-child": { pb: 0 } }}>
          {loading ? (
            <Box sx={{ display: "flex", justifyContent: "center", p: 8 }}>
              <CircularProgress />
            </Box>
          ) : files.length === 0 ? (
            <Box sx={{ py: 12, textAlign: "center", color: "text.secondary" }}>
              <CloudUploadIcon sx={{ fontSize: 60, mb: 2, opacity: 0.3 }} />
              <Typography variant="h6">No files uploaded yet</Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>Upload a file to securely store it in MinIO object storage</Typography>
            </Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead sx={{ bgcolor: "background.default" }}>
                  <TableRow>
                    <TableCell>Filename</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Size</TableCell>
                    <TableCell>Uploaded On</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {files.map((file) => (
                    <TableRow key={file.id} hover>
                      <TableCell sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                        <FileIcon color="action" />
                        <Typography variant="body2" fontWeight="medium">
                          {file.filename}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip size="small" label={file.content_type.split("/")[1] || "File"} variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {formatBytes(file.size_bytes)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary" suppressHydrationWarning>
                          {formatDate(file.created_at)}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <IconButton 
                          color="primary" 
                          onClick={() => handleDownload(file.id, file.filename)}
                          title="Generate MinIO URL and Download"
                        >
                          <DownloadIcon />
                        </IconButton>
                        <IconButton 
                          color="error" 
                          onClick={() => handleDelete(file.id, file.filename)}
                          title="Delete permanently"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      <Snackbar open={!!error} autoHideDuration={6000} onClose={() => setError(null)}>
        <Alert onClose={() => setError(null)} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
      
      <Snackbar open={!!successMsg} autoHideDuration={4000} onClose={() => setSuccessMsg(null)}>
        <Alert onClose={() => setSuccessMsg(null)} severity="success" sx={{ width: '100%' }}>
          {successMsg}
        </Alert>
      </Snackbar>
    </Box>
  );
}
