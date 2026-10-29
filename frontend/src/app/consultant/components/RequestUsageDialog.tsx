"use client";

import GroupsOutlinedIcon from "@mui/icons-material/GroupsOutlined";
import PersonOutlineOutlinedIcon from "@mui/icons-material/PersonOutlineOutlined";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Button from "@mui/material/Button";
import Divider from "@mui/material/Divider";
import LinearProgress from "@mui/material/LinearProgress";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useEffect, type ReactNode } from "react";

import { useUsage } from "@/context/UsageContext";
import type { UsageResponse } from "@/types/api";

type RequestUsageDialogProps = {
  open: boolean;
  onClose: () => void;
  usageOverride?: UsageResponse;
};

function formatResetTime(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function usedPercent(used: number, limit: number) {
  return limit > 0 ? Math.min(100, (used / limit) * 100) : 0;
}

type QuotaBlockProps = {
  icon: ReactNode;
  label: string;
  remaining: number;
  limit: number;
  used: number;
  description: string;
};

/** One allowance (personal or shared); both use the same layout so neither reads as secondary. */
function QuotaBlock({ icon, label, remaining, limit, used, description }: QuotaBlockProps) {
  const percent = usedPercent(used, limit);
  return (
    <Stack spacing={0.75}>
      <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
        <Box sx={{ display: "flex", color: "text.secondary" }}>{icon}</Box>
        <Typography variant="body1" sx={{ fontWeight: 700, flexGrow: 1 }}>
          {label}
        </Typography>
        <Typography variant="body1" sx={{ fontWeight: 700, fontVariantNumeric: "tabular-nums" }}>
          {remaining} / {limit} left
        </Typography>
      </Stack>
      <LinearProgress
        variant="determinate"
        value={percent}
        color={percent >= 80 ? "warning" : "primary"}
        aria-label={`${label}: ${remaining} of ${limit} requests left`}
      />
      <Typography variant="body2" sx={{ color: "text.secondary" }}>
        {description}
      </Typography>
    </Stack>
  );
}

export function RequestUsageDialog({
  open,
  onClose,
  usageOverride,
}: RequestUsageDialogProps) {
  const { usage, isLoading, error, refreshUsage } = useUsage();

  useEffect(() => {
    if (open && !usageOverride) {
      void refreshUsage();
    }
  }, [open, refreshUsage, usageOverride]);

  const displayedUsage = usageOverride ?? usage;
  const displayedIsLoading = usageOverride ? false : isLoading;
  const displayedError = usageOverride ? null : error;
  const service = displayedUsage?.service;

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="xs" aria-labelledby="usage-title">
      <DialogTitle id="usage-title">Daily request allowance</DialogTitle>
      <DialogContent>
        {displayedUsage ? (
          <Stack spacing={2.5}>
            <QuotaBlock
              icon={<PersonOutlineOutlinedIcon fontSize="small" />}
              label="You"
              remaining={displayedUsage.remaining}
              limit={displayedUsage.limit}
              used={displayedUsage.used}
              description="Your personal limit (per IP address)."
            />

            {service && (
              <QuotaBlock
                icon={<GroupsOutlinedIcon fontSize="small" />}
                label="All users (shared)"
                remaining={service.remaining}
                limit={service.limit}
                used={service.used}
                description="Shared by everyone. If it runs out, nobody can send requests until the reset."
              />
            )}

            {service && service.remaining <= 0 && (
              <Alert severity="warning">
                The shared limit is used up, so requests will fail until it resets — even though you
                have {displayedUsage.remaining} of your own left.
              </Alert>
            )}

            <Divider />
            <Typography variant="body2" sx={{ color: "text.secondary" }}>
              A chat message or transcript upload uses 1 request
              {service ? " from both" : ""}. {service ? "Both reset" : "Resets"} on{" "}
              {formatResetTime(displayedUsage.reset_at)}.
            </Typography>
          </Stack>
        ) : (
          <Typography variant="body2" sx={{ color: displayedError ? "error.main" : "text.secondary" }}>
            {displayedError ?? (
              displayedIsLoading ? "Loading daily request allowance…" : "Daily request allowance unavailable."
            )}
          </Typography>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
}
