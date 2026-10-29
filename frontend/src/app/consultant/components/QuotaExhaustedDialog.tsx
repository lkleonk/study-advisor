"use client";

import CheckIcon from "@mui/icons-material/Check";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Checkbox from "@mui/material/Checkbox";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import FormControlLabel from "@mui/material/FormControlLabel";
import Stack from "@mui/material/Stack";
import { useEffect, useState } from "react";

import { useDegree } from "@/context/DegreeContext";
import { getProgramRules } from "@/services/api";
import type { ProgramRulesCatalogue } from "@/types/api";

import type { ChatMessage } from "./chatMessages";
import { buildDegreeRulesText } from "./degreeRulesText";

function formatResetTime(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

/** Whose allowance ran out: the visitor's own, or the shared one for everyone. */
export type QuotaExhaustedScope = "user" | "service";

type QuotaExhaustedDialogProps = {
  open: boolean;
  scope: QuotaExhaustedScope;
  resetAt: string | null;
  conversation: ChatMessage[];
  onClose: () => void;
  onOpenDegreeRules: () => void;
};

export function QuotaExhaustedDialog({
  open,
  scope,
  resetAt,
  conversation,
  onClose,
  onOpenDegreeRules,
}: QuotaExhaustedDialogProps) {
  const { effectiveDegreeId } = useDegree();
  const [includeConversation, setIncludeConversation] = useState(false);
  const [catalogue, setCatalogue] = useState<ProgramRulesCatalogue | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load the rules when the dialog opens, so the click can write to the
  // clipboard immediately; browsers (notably Safari) reject clipboard writes
  // that happen after awaiting a request.
  useEffect(() => {
    if (!open) {
      return;
    }
    let cancelled = false;
    getProgramRules(effectiveDegreeId)
      .then((loaded) => {
        if (!cancelled) setCatalogue(loaded);
      })
      .catch(() => {
        if (!cancelled) setError("Could not load the degree rules. Open Degree Rules instead.");
      });
    return () => {
      cancelled = true;
    };
  }, [effectiveDegreeId, open]);

  const until = resetAt ? ` until ${formatResetTime(resetAt)}` : " until the daily allowance resets";

  const copyDegreeRules = async () => {
    if (!catalogue) return;
    setError(null);
    try {
      await navigator.clipboard.writeText(
        buildDegreeRulesText(catalogue, includeConversation ? conversation : []),
      );
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setError("Could not copy to the clipboard. Your browser may block it here.");
    }
  };

  return (
    <Dialog open={open} onClose={onClose} aria-labelledby="quota-exhausted-title">
      <DialogTitle id="quota-exhausted-title">Daily limit reached — continue elsewhere</DialogTitle>
      <DialogContent>
        <DialogContentText>
          {scope === "service"
            ? `Modulio has used up today's capacity for everyone, so chat and transcript checks are paused${until}.`
            : `You have used all of your requests for today, so chat and transcript checks are paused${until}.`}
        </DialogContentText>
        <DialogContentText sx={{ mt: 1.5 }}>
          Copy the rules for your degree and paste them into ChatGPT, Claude or Gemini to keep
          asking there. Degree Rules and the Course Registry stay available here.
        </DialogContentText>
        <Stack
          direction={{ xs: "column", sm: "row" }}
          spacing={1.5}
          sx={{
            mt: 2,
            p: 1.5,
            border: 1,
            borderColor: "divider",
            borderRadius: 1,
            alignItems: { xs: "flex-start", sm: "center" },
          }}
        >
          <Button
            variant="contained"
            startIcon={copied ? <CheckIcon /> : <ContentCopyIcon />}
            onClick={() => void copyDegreeRules()}
            disabled={!catalogue}
            sx={{ flexShrink: 0 }}
          >
            {copied ? "Copied" : "Copy degree rules"}
          </Button>
          {conversation.length > 0 && (
            <FormControlLabel
              control={
                <Checkbox
                  checked={includeConversation}
                  onChange={(event) => setIncludeConversation(event.target.checked)}
                />
              }
              label="Include our conversation so far"
            />
          )}
        </Stack>
        {error && (
          <Alert severity="error" sx={{ mt: 1 }}>
            {error}
          </Alert>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
        <Button onClick={onOpenDegreeRules}>Go to Degree Rules</Button>
      </DialogActions>
    </Dialog>
  );
}
