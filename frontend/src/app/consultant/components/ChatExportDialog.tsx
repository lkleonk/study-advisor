"use client";

import DescriptionOutlinedIcon from "@mui/icons-material/DescriptionOutlined";
import TextSnippetOutlinedIcon from "@mui/icons-material/TextSnippetOutlined";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import Stack from "@mui/material/Stack";

import type { ChatExportFormat } from "./chatExport";
import type { ChatMessage } from "./chatMessages";

type ChatExportDialogProps = {
  open: boolean;
  messages: ChatMessage[];
  onClose: () => void;
  onDownload: (format: ChatExportFormat) => void;
};

export function ChatExportDialog({ open, messages, onClose, onDownload }: ChatExportDialogProps) {
  return (
    <Dialog open={open} fullWidth maxWidth="xs" onClose={onClose} aria-labelledby="chat-export-title">
      <DialogTitle id="chat-export-title">Download chat</DialogTitle>
      <DialogContent>
        <DialogContentText>
          Choose a file format for this {messages.length}-message conversation.
        </DialogContentText>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={1} sx={{ width: "100%" }}>
          <Button
            fullWidth
            variant="contained"
            startIcon={<DescriptionOutlinedIcon />}
            onClick={() => onDownload("markdown")}
            sx={[
              {
                bgcolor: "primary.main",
                color: "primary.contrastText",
                "&:hover": { bgcolor: "primary.dark" },
              },
              (theme) =>
                theme.applyStyles("dark", {
                  bgcolor: "primary.dark",
                  color: "common.white",
                }),
            ]}
          >
            Markdown (.md)
          </Button>
          <Button
            fullWidth
            variant="outlined"
            startIcon={<TextSnippetOutlinedIcon />}
            onClick={() => onDownload("text")}
            sx={[
              {
                color: "primary.main",
                borderColor: "primary.dark",
                "&:hover": {
                  borderColor: "primary.dark",
                  bgcolor: "primary.light",
                },
              },
              (theme) =>
                theme.applyStyles("dark", {
                  color: "common.white",
                  "&:hover": { bgcolor: "primary.dark" },
                }),
            ]}
          >
            Plain text (.txt)
          </Button>
        </Stack>
      </DialogActions>
    </Dialog>
  );
}
