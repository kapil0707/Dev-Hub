"use client";

import { useEffect, useState } from "react";
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  IconButton,
  Tooltip,
} from "@mui/material";
import {
  PlayArrow as PlayIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  Terminal as TerminalIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  HourglassEmpty as PendingIcon,
} from "@mui/icons-material";
import { Execution, getExecutions, runScript } from "@/lib/api/automation";
import { trackEvent } from "@/lib/api/analytics";

export default function AutomationHubPage() {
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [loading, setLoading] = useState(true);
  const [openDialog, setOpenDialog] = useState(false);
  const [scriptContent, setScriptContent] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    trackEvent("page_view", { page: "automation" });
  }, []);

  // Fetch executions
  const loadExecutions = async () => {
    setLoading(true);
    try {
      const data = await getExecutions();
      setExecutions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExecutions();
  }, []);

  // Handle Form Submit
  const handleRunScript = async () => {
    if (!scriptContent.trim()) return;

    setIsSubmitting(true);
    try {
      await runScript(scriptContent);
      trackEvent("script_execution", { length: scriptContent.length });
      setOpenDialog(false);
      setScriptContent("");
      await loadExecutions(); // Refresh the list
    } catch (err) {
      console.error(err);
      alert(err instanceof Error ? err.message : "Failed to run script");
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusChip = (status: string) => {
    switch (status) {
      case "Success":
        return <Chip icon={<SuccessIcon />} label="Success" size="small" color="success" sx={{ bgcolor: "rgba(34, 197, 94, 0.1)", color: "#4ADE80" }} />;
      case "Failed":
        return <Chip icon={<ErrorIcon />} label="Failed" size="small" color="error" sx={{ bgcolor: "rgba(239, 68, 68, 0.1)", color: "#F87171" }} />;
      case "Pending":
      default:
        return <Chip icon={<PendingIcon />} label="Pending" size="small" color="warning" sx={{ bgcolor: "rgba(245, 158, 11, 0.1)", color: "#FBBF24" }} />;
    }
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: "auto" }}>
      {/* Header */}
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4 }}>
        <Box>
          <Typography variant="h4" sx={{ color: "#F1F5F9", fontWeight: 700 }}>
            Automation Hub
          </Typography>
          <Typography variant="body2" sx={{ color: "#94A3B8", mt: 0.5 }}>
            Execute local shell scripts and view execution history.
          </Typography>
        </Box>
        <Box sx={{ display: "flex", gap: 2 }}>
          <Tooltip title="Refresh">
            <IconButton onClick={loadExecutions} sx={{ color: "#06B6D4", bgcolor: "rgba(6, 182, 212, 0.1)", "&:hover": { bgcolor: "rgba(6, 182, 212, 0.2)" } }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog(true)}
            sx={{
              bgcolor: "#06B6D4",
              color: "#0F172A",
              fontWeight: 600,
              textTransform: "none",
              borderRadius: 2,
              "&:hover": { bgcolor: "#0891B2" },
            }}
          >
            New Automation
          </Button>
        </Box>
      </Box>

      {/* Executions Table */}
      <Card sx={{ bgcolor: "rgba(30, 41, 59, 0.6)", border: "1px solid rgba(148, 163, 184, 0.08)", borderRadius: 3 }}>
        <CardContent sx={{ p: 0 }}>
          <TableContainer>
            <Table>
              <TableHead sx={{ bgcolor: "rgba(15, 23, 42, 0.5)" }}>
                <TableRow>
                  <TableCell sx={{ color: "#94A3B8", fontWeight: 600, borderBottom: "1px solid rgba(148, 163, 184, 0.08)" }}>Script Name / Content</TableCell>
                  <TableCell align="center" sx={{ color: "#94A3B8", fontWeight: 600, borderBottom: "1px solid rgba(148, 163, 184, 0.08)" }}>Status</TableCell>
                  <TableCell align="center" sx={{ color: "#94A3B8", fontWeight: 600, borderBottom: "1px solid rgba(148, 163, 184, 0.08)" }}>Exit Code</TableCell>
                  <TableCell align="right" sx={{ color: "#94A3B8", fontWeight: 600, borderBottom: "1px solid rgba(148, 163, 184, 0.08)" }}>Executed At</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={4} align="center" sx={{ py: 6, borderBottom: "none" }}>
                      <CircularProgress size={32} sx={{ color: "#06B6D4" }} />
                    </TableCell>
                  </TableRow>
                ) : executions.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} align="center" sx={{ py: 6, color: "#64748B", borderBottom: "none" }}>
                      No scripts executed yet. Click "New Automation" to start.
                    </TableCell>
                  </TableRow>
                ) : (
                  executions.map((exec) => (
                    <TableRow key={exec.id} hover sx={{ "&:last-child td, &:last-child th": { border: 0 }, "&:hover": { bgcolor: "rgba(255, 255, 255, 0.02)" } }}>
                      <TableCell sx={{ borderBottom: "1px solid rgba(148, 163, 184, 0.08)" }}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
                          <TerminalIcon sx={{ color: "#64748B", fontSize: 20 }} />
                          <Typography variant="body2" sx={{ color: "#E2E8F0", fontFamily: "monospace", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: { xs: 150, sm: 300, md: 500 } }}>
                            {exec.script_content.split('\n')[0]}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="center" sx={{ borderBottom: "1px solid rgba(148, 163, 184, 0.08)" }}>
                        {getStatusChip(exec.status)}
                      </TableCell>
                      <TableCell align="center" sx={{ color: "#94A3B8", borderBottom: "1px solid rgba(148, 163, 184, 0.08)" }}>
                        {exec.exit_code !== null ? exec.exit_code : "—"}
                      </TableCell>
                      <TableCell align="right" sx={{ color: "#64748B", borderBottom: "1px solid rgba(148, 163, 184, 0.08)" }}>
                        {new Date(exec.created_at).toLocaleString()}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* New Script Dialog */}
      {isMounted && (
        <Dialog
          open={openDialog}
          onClose={() => !isSubmitting && setOpenDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            bgcolor: "#0F172A",
            border: "1px solid rgba(148, 163, 184, 0.1)",
            backgroundImage: "none",
            borderRadius: 3,
          },
        }}
      >
        <DialogTitle sx={{ color: "#F1F5F9", display: "flex", alignItems: "center", gap: 1 }}>
          <PlayIcon sx={{ color: "#06B6D4" }} /> Run Shell Script
        </DialogTitle>
        <DialogContent sx={{ py: 2 }}>
          <Typography variant="body2" sx={{ color: "#94A3B8", mb: 2 }}>
            Write the bash or shell script you want to execute on the local machine.
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={10}
            variant="outlined"
            placeholder="#!/bin/bash\necho 'Hello World'\npwd"
            value={scriptContent}
            onChange={(e) => setScriptContent(e.target.value)}
            disabled={isSubmitting}
            InputProps={{
              sx: {
                fontFamily: "monospace",
                color: "#E2E8F0",
                bgcolor: "rgba(15, 23, 42, 0.6)",
                "& fieldset": { borderColor: "rgba(148, 163, 184, 0.2)" },
                "&:hover fieldset": { borderColor: "rgba(148, 163, 184, 0.3)" },
                "&.Mui-focused fieldset": { borderColor: "#06B6D4" },
              },
            }}
          />
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 0 }}>
          <Button onClick={() => setOpenDialog(false)} disabled={isSubmitting} sx={{ color: "#94A3B8" }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            disabled={!scriptContent.trim() || isSubmitting}
            onClick={handleRunScript}
            startIcon={isSubmitting ? <CircularProgress size={20} color="inherit" /> : <PlayIcon />}
            sx={{
              bgcolor: "#06B6D4",
              color: "#0F172A",
              fontWeight: 600,
              "&:hover": { bgcolor: "#0891B2" },
              "&.Mui-disabled": { bgcolor: "rgba(6, 182, 212, 0.3)", color: "rgba(15, 23, 42, 0.5)" },
            }}
          >
            {isSubmitting ? "Running..." : "Execute"}
          </Button>
        </DialogActions>
      </Dialog>
      )}
    </Box>
  );
}
