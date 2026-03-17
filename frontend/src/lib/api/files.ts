export interface FileRecord {
  id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  created_at: string;
}

export const fileApi = {
  async getFiles(): Promise<FileRecord[]> {
    const res = await fetch("http://localhost:8000/api/v1/files", {
      credentials: "include",
    });
    if (!res.ok) {
      if (res.status === 401) throw new Error("Unauthorized");
      throw new Error(`Failed to fetch files: ${res.statusText}`);
    }
    return res.json();
  },

  async uploadFile(file: File): Promise<any> {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://localhost:8000/api/v1/files/upload", {
      method: "POST",
      body: formData,
      credentials: "include",
    });
    if (!res.ok) throw new Error("Failed to upload file");
    return res.json();
  },

  async deleteFile(id: string): Promise<void> {
    const res = await fetch(`http://localhost:8000/api/v1/files/${id}`, {
      method: "DELETE",
      credentials: "include",
    });
    if (!res.ok) throw new Error("Failed to delete file");
  },

  async downloadFile(id: string, filename: string): Promise<void> {
    const res = await fetch(`http://localhost:8000/api/v1/files/${id}/download`, {
      credentials: "include",
    });
    if (!res.ok) throw new Error("Failed to fetch download URL");
    
    const data = await res.json();
    
    // Create an anchor pointing to the pre-signed MinIO URL and trigger download
    const a = document.createElement("a");
    a.href = data.url;
    a.download = filename;
    a.target = "_blank"; // Provide a fallback if purely cross-origin
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
};
