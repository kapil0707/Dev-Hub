/**
 * =============================================================================
 * Login Page — /login
 * =============================================================================
 * A centered card with email + password fields and a gradient submit button.
 * On success: BFF sets httpOnly cookie → AuthContext loads user → redirect
 * On error: shows MUI Snackbar with the error message
 *
 * DESIGN CHOICES:
 *   - Centered vertically + horizontally with a max-width card
 *   - Subtle background gradient (navy → darker navy)
 *   - "DevHub" branding with Terminal icon at the top
 *   - Minimal form: email + password + submit — no distractions
 * =============================================================================
 */
"use client";

import { useState, FormEvent } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton,
  Stack,
} from "@mui/material";
import {
  Terminal as TerminalIcon,
  Visibility,
  VisibilityOff,
  Email as EmailIcon,
  Lock as LockIcon,
  Person as PersonIcon,
} from "@mui/icons-material";
import { useAuth } from "@/contexts/AuthContext";

export default function LoginPage() {
  const { login, register } = useAuth();
  const [isRegistering, setIsRegistering] = useState(false);
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (isRegistering) {
        await register(email, displayName, password);
      } else {
        await login(email, password);
      }
    } catch (err: unknown) {
      // Axios wraps the error response
      const axiosErr = err as { response?: { data?: { detail?: string | any[] } } };
      let errMsg = isRegistering ? "Registration failed" : "Login failed — check your credentials";
      if (axiosErr.response?.data?.detail) {
        const detail = axiosErr.response.data.detail;
        errMsg = Array.isArray(detail) ? detail[0].msg : detail;
      }
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #0B1120 0%, #1E293B 50%, #0B1120 100%)",
        p: 2,
      }}
    >
      <Card
        sx={{
          maxWidth: 440,
          width: "100%",
          bgcolor: "rgba(30, 41, 59, 0.7)",
          backdropFilter: "blur(20px)",
          border: "1px solid rgba(148, 163, 184, 0.1)",
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.5)",
        }}
      >
        <CardContent sx={{ p: 4 }}>
          {/* Branding */}
          <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 1 }}>
            <Box
              sx={{
                width: 44,
                height: 44,
                borderRadius: 2,
                background: "linear-gradient(135deg, #06B6D4, #8B5CF6)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <TerminalIcon sx={{ color: "#fff", fontSize: 24 }} />
            </Box>
            <Typography variant="h5" sx={{ fontWeight: 700, color: "#F1F5F9" }}>
              DevHub
            </Typography>
          </Stack>

          <Typography variant="body2" sx={{ mb: 4, color: "#94A3B8" }}>
            {isRegistering ? "Create a new developer account" : "Sign in to your developer dashboard"}
          </Typography>

          {/* Error Alert */}
          {error && (
            <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
              {error}
            </Alert>
          )}

          {/* Login Form */}
          <Box component="form" onSubmit={handleSubmit} noValidate>
            {isRegistering && (
              <TextField
                id="displayName"
                label="Display Name"
                fullWidth
                required
                autoFocus
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                sx={{ mb: 2.5 }}
                slotProps={{
                  input: {
                    startAdornment: (
                      <InputAdornment position="start">
                        <PersonIcon sx={{ color: "#64748B", fontSize: 20 }} />
                      </InputAdornment>
                    ),
                  },
                }}
              />
            )}
            <TextField
              id="email"
              label="Email"
              type="email"
              fullWidth
              required
              autoFocus={!isRegistering}
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              sx={{ mb: 2.5 }}
              slotProps={{
                input: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <EmailIcon sx={{ color: "#64748B", fontSize: 20 }} />
                    </InputAdornment>
                  ),
                },
              }}
            />

            <TextField
              id="password"
              label="Password"
              type={showPassword ? "text" : "password"}
              fullWidth
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              sx={{ mb: 3 }}
              slotProps={{
                input: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <LockIcon sx={{ color: "#64748B", fontSize: 20 }} />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                        size="small"
                        aria-label="toggle password visibility"
                      >
                        {showPassword ? (
                          <VisibilityOff sx={{ fontSize: 20 }} />
                        ) : (
                          <Visibility sx={{ fontSize: 20 }} />
                        )}
                      </IconButton>
                    </InputAdornment>
                  ),
                },
              }}
            />

            <Button
              id="login-submit"
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading || !email || !password || (isRegistering && !displayName)}
              sx={{
                py: 1.5,
                fontSize: "1rem",
                position: "relative",
              }}
            >
              {loading ? (
                <CircularProgress size={24} sx={{ color: "#fff" }} />
              ) : (
                isRegistering ? "Sign Up" : "Sign In"
              )}
            </Button>
            
            <Box sx={{ mt: 3, textAlign: "center" }}>
              <Typography variant="body2" component="span" sx={{ color: "#64748B" }}>
                {isRegistering ? "Already have an account?" : "Don't have an account?"}{" "}
              </Typography>
              <Button
                  variant="text"
                  onClick={() => {
                    setIsRegistering(!isRegistering);
                    setError("");
                  }}
                  sx={{ color: "#06B6D4", textTransform: "none", p: 0, minWidth: "auto", "&:hover": { bgcolor: "transparent", textDecoration: "underline" } }}
                >
                  {isRegistering ? "Sign In" : "Sign Up"}
                </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
