"use client";

import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import DataUsageOutlinedIcon from "@mui/icons-material/DataUsageOutlined";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import SendOutlinedIcon from "@mui/icons-material/SendOutlined";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import CircularProgress from "@mui/material/CircularProgress";
import Collapse from "@mui/material/Collapse";
import IconButton from "@mui/material/IconButton";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { useDegree } from "@/context/DegreeContext";
import { useSettings } from "@/context/SettingsContext";
import { useUsage } from "@/context/UsageContext";
import { createSession, quotaErrorCode, sendMessage } from "@/services/api";
import type { RuleCheckResult, StudyPlan, TranscriptUploadResponse } from "@/types/api";

import {
  buildTranscriptChatMessages,
  createMessageId,
  loadStoredChatMessages,
  type ChatMessage,
} from "./chatMessages";
import { CitationList } from "./CitationList";
import { ChatErrorDialog, DEFAULT_CHAT_ERROR_MESSAGE } from "./ChatErrorDialog";
import { LinkifiedText } from "./LinkifiedText";
import { issueChipSx, RuleCheckPanel } from "./RuleCheckPanel";
import { TranscriptUpload } from "./TranscriptUpload";
import { CHAT_MESSAGES_STORAGE_KEY, SESSION_ID_STORAGE_KEY } from "./storage";

type ChatTabProps = {
  sessionId: string | null;
  onSessionIdChange: (sessionId: string | null) => void;
  onRuleCheckResult: (result: RuleCheckResult | null) => void;
  onStudyPlan: (plan: StudyPlan | null) => void;
  onMessagesChange: (messages: ChatMessage[]) => void;
  onOpenUsage: () => void;
  onDownloadChat: () => void;
  onContinueElsewhere: () => void;
};

function formatResetTime(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatResetTimeShort(value: string) {
  return new Intl.DateTimeFormat(undefined, { timeStyle: "short" }).format(new Date(value));
}

function countRuleIssues(result: RuleCheckResult) {
  return {
    issues: result.issues.filter((issue) => issue.severity === "error").length,
    warnings: result.issues.filter((issue) => issue.severity === "warning").length,
  };
}

export function ChatTab({
  sessionId,
  onSessionIdChange,
  onRuleCheckResult,
  onStudyPlan,
  onMessagesChange,
  onOpenUsage,
  onDownloadChat,
  onContinueElsewhere,
}: ChatTabProps) {
  const { usage, updateQuota, noteApiError } = useUsage();
  const { effectiveDegreeId, degrees } = useDegree();
  const currentDegree = degrees.find((degree) => degree.id === effectiveDegreeId);
  const { tracingEnabled } = useSettings();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errorDialogOpen, setErrorDialogOpen] = useState(false);
  const [expandedRuleMessageId, setExpandedRuleMessageId] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const hasLoadedStoredMessages = useRef(false);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      const storedMessages = loadStoredChatMessages();
      setMessages(storedMessages);
      const reversed = [...storedMessages].reverse();
      const latestRuleCheck = reversed.find((message) => message.ruleCheckResult)?.ruleCheckResult;
      const latestStudyPlan = reversed.find((message) => message.parsedStudyPlan)?.parsedStudyPlan;
      onRuleCheckResult(latestRuleCheck ?? null);
      onStudyPlan(latestStudyPlan ?? null);
      hasLoadedStoredMessages.current = true;
    }, 0);

    return () => window.clearTimeout(timer);
  }, [onRuleCheckResult, onStudyPlan]);

  useEffect(() => {
    if (!hasLoadedStoredMessages.current) {
      return;
    }
    window.sessionStorage.setItem(CHAT_MESSAGES_STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    onMessagesChange(messages);
  }, [messages, onMessagesChange]);

  useEffect(() => {
    if (sessionId) {
      window.sessionStorage.setItem(SESSION_ID_STORAGE_KEY, sessionId);
    }
  }, [sessionId]);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, isLoading]);

  // Shown only while the caller still has own requests; otherwise the own limit is the reason.
  const serviceExhausted =
    usage !== null && usage.remaining > 0 && usage.service.remaining <= 0;
  const quotaExhausted = usage !== null && (usage.remaining <= 0 || serviceExhausted);
  const canSend = useMemo(
    () => input.trim().length > 0 && !isLoading && !quotaExhausted,
    [input, isLoading, quotaExhausted],
  );

  const showError = useCallback((message: string) => {
    setError(message);
    setErrorDialogOpen(true);
  }, []);

  const ensureSession = useCallback(async () => {
    if (sessionId) {
      return sessionId;
    }

    const created = await createSession(effectiveDegreeId);
    onSessionIdChange(created.session_id);
    window.sessionStorage.setItem(SESSION_ID_STORAGE_KEY, created.session_id);
    return created.session_id;
  }, [effectiveDegreeId, onSessionIdChange, sessionId]);

  const handleSubmit = useCallback(async () => {
    const content = input.trim();
    if (!content || isLoading || quotaExhausted) {
      return;
    }

    setError(null);
    setErrorDialogOpen(false);
    setInput("");
    setIsLoading(true);

    const userMessage: ChatMessage = {
      id: createMessageId(),
      role: "user",
      content,
    };
    setMessages((current) => [...current, userMessage]);

    try {
      const activeSessionId = await ensureSession();
      const response = await sendMessage(activeSessionId, content, tracingEnabled);
      updateQuota(response.usage);
      const reply = response.data;
      const assistantMessage: ChatMessage = {
        id: createMessageId(),
        role: "assistant",
        content: reply.reply,
        messageType: reply.message_type,
        citations: reply.citations,
        ruleCheckResult: reply.rule_check_result,
        parsedStudyPlan: reply.parsed_study_plan,
      };

      setMessages((current) => [...current, assistantMessage]);
      onRuleCheckResult(reply.rule_check_result);
      if (reply.parsed_study_plan) {
        onStudyPlan(reply.parsed_study_plan);
      }
    } catch (sendError) {
      noteApiError(sendError);
      if (quotaErrorCode(sendError)) {
        // The quota dialog explains this; no extra error dialog.
        return;
      }
      showError(sendError instanceof Error ? sendError.message : "The message could not be sent.");
    } finally {
      setIsLoading(false);
    }
  }, [
    ensureSession,
    input,
    isLoading,
    noteApiError,
    onRuleCheckResult,
    onStudyPlan,
    quotaExhausted,
    showError,
    tracingEnabled,
    updateQuota,
  ]);

  const handleTranscriptUploaded = useCallback(
    (result: TranscriptUploadResponse) => {
      setError(null);
      setMessages((current) => [...current, ...buildTranscriptChatMessages(result)]);
      onRuleCheckResult(result.rule_check_result);
      if (result.parsed_study_plan) {
        onStudyPlan(result.parsed_study_plan);
      }
    },
    [onRuleCheckResult, onStudyPlan],
  );

  return (
    <Box sx={{ height: "100%", minHeight: 0, display: "flex", flexDirection: "column" }}>
      <Box
        sx={{
          flexShrink: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "flex-end",
          gap: 1,
          px: { xs: 1.5, md: 3 },
          py: 0.75,
          borderBottom: 1,
          borderColor: "divider",
          bgcolor: "background.paper",
        }}
      >
        <Tooltip
          title="Unofficial tool, not affiliated with FU Berlin. Answers may be incomplete or incorrect. Please verify important information using official FU Berlin regulations or the responsible advising office."
          enterTouchDelay={0}
          leaveTouchDelay={6000}
        >
          <Stack
            component="aside"
            aria-label="Unofficial service notice"
            tabIndex={0}
            direction="row"
            spacing={0.5}
            sx={{
              mr: "auto",
              minWidth: 0,
              alignItems: "center",
              color: "text.secondary",
              cursor: "help",
            }}
          >
            <InfoOutlinedIcon sx={{ fontSize: 16, flexShrink: 0 }} />
            <Typography variant="caption" noWrap>
              {/* Longer wording as width allows; the tooltip always holds the full notice. */}
              <Box component="span" sx={{ display: { xs: "inline", md: "none" } }}>
                Unofficial tool
              </Box>
              <Box component="span" sx={{ display: { xs: "none", md: "inline", lg: "none" } }}>
                Unofficial tool, not affiliated with FU Berlin · verify important info
              </Box>
              <Box component="span" sx={{ display: { xs: "none", lg: "inline" } }}>
                Unofficial tool, not affiliated with FU Berlin. Answers may be incomplete or
                incorrect, so please verify important information.
              </Box>
            </Typography>
          </Stack>
        </Tooltip>
        <Tooltip title="Your chat isn't saved. Download it if you want to keep a copy.">
          <span>
            <Button
              size="small"
              variant="text"
              startIcon={<DownloadOutlinedIcon fontSize="small" />}
              disabled={messages.length === 0}
              onClick={onDownloadChat}
              aria-label="Download chat"
              sx={{
                minWidth: 0,
                "& .MuiButton-startIcon": { mr: { xs: 0, sm: 1 }, ml: { xs: 0, sm: -0.5 } },
              }}
            >
              <Box component="span" sx={{ display: { xs: "none", sm: "inline" } }}>
                Download
              </Box>
            </Button>
          </span>
        </Tooltip>
        <Tooltip
          title={
            serviceExhausted
              ? `Modulio's shared daily capacity is used up for everyone. Your own ${usage.remaining} of ${usage.limit} requests stay for after the reset.`
              : usage
                ? `${usage.remaining} of ${usage.limit} daily requests left`
                : "Daily request allowance"
          }
        >
          <Chip
            icon={<DataUsageOutlinedIcon />}
            label={
              serviceExhausted ? (
                <>
                  Service limit reached
                  <Box component="span" sx={{ display: { xs: "none", sm: "inline" } }}>
                    {" "}· resets {formatResetTimeShort(usage.reset_at)}
                  </Box>
                </>
              ) : usage ? (
                <>
                  <Box component="span" sx={{ display: { xs: "none", sm: "inline" } }}>
                    Usage:{" "}
                  </Box>
                  {usage.remaining}/{usage.limit}
                  <Box component="span" sx={{ display: { xs: "none", sm: "inline" } }}>
                    {" "}requests · resets {formatResetTimeShort(usage.reset_at)}
                  </Box>
                </>
              ) : (
                "Usage —"
              )
            }
            color={
              usage && (usage.remaining <= 0 || serviceExhausted)
                ? "error"
                : usage && usage.remaining <= 10
                  ? "warning"
                  : "default"
            }
            onClick={onOpenUsage}
            clickable
            size="small"
          />
        </Tooltip>
      </Box>
      <Box
        ref={scrollRef}
        sx={{
          flex: 1,
          minHeight: 0,
          overflowY: "auto",
          px: { xs: 1.5, md: 3 },
          py: 2,
        }}
      >
        <Stack spacing={1.5}>
          {messages.length === 0 && (
            <Paper variant="outlined" sx={{ p: 2, bgcolor: "background.paper" }}>
              <Typography variant="h2" sx={{ mb: 0.75 }}>
                FU Berlin {currentDegree?.display_name ?? "study consultant"}
              </Typography>
              <Typography variant="body2" sx={{ color: "text.secondary" }}>
                {currentDegree?.plan_validation_enabled
                  ? "Ask a study-rule question or paste a draft study plan."
                  : "Ask a study-rule or course question, or upload your transcript PDF."}
              </Typography>
            </Paper>
          )}

          {messages.map((message) => {
            const isUser = message.role === "user";
            const ruleCheckResult =
              !isUser && message.messageType === "plan_check" ? message.ruleCheckResult : null;
            const isRuleExpanded = expandedRuleMessageId === message.id;
            const ruleIssueCounts = ruleCheckResult ? countRuleIssues(ruleCheckResult) : null;

            return (
              <Box
                key={message.id}
                sx={{
                  display: "flex",
                  justifyContent: isUser ? "flex-end" : "flex-start",
                }}
              >
                <Paper
                  variant="outlined"
                  sx={[
                    {
                      p: 1.5,
                      maxWidth: { xs: "90%", md: "75%" },
                      bgcolor: isUser ? "primary.main" : "background.paper",
                      color: isUser ? "primary.contrastText" : "text.primary",
                      borderColor: isUser ? "primary.dark" : "divider",
                    },
                    isUser &&
                      ((theme) =>
                        theme.applyStyles("dark", {
                          bgcolor: "primary.dark",
                          color: "common.white",
                        })),
                  ]}
                >
                  <Typography
                    variant="caption"
                    sx={{
                      display: "block",
                      mb: 0.5,
                      fontWeight: 700,
                      color: isUser ? "inherit" : "text.secondary",
                    }}
                  >
                    {isUser ? "You" : "Assistant"}
                  </Typography>
                  <Box sx={{ typography: "body1" }}>
                    <LinkifiedText
                      text={message.content}
                      linkColor={isUser ? "inherit" : undefined}
                    />
                  </Box>
                  {!isUser && <CitationList citations={message.citations ?? []} />}
                  {ruleCheckResult && ruleIssueCounts && (
                    <Box
                      sx={{
                        mt: 1.5,
                        p: 1,
                        border: 1,
                        borderColor: "divider",
                        borderRadius: 1,
                        bgcolor: "action.hover",
                      }}
                    >
                      <Stack
                        direction={{ xs: "column", sm: "row" }}
                        spacing={1}
                        sx={{
                          alignItems: { xs: "flex-start", sm: "center" },
                          justifyContent: "space-between",
                        }}
                      >
                        <Stack direction="row" spacing={0.75} sx={{ alignItems: "center", flexWrap: "wrap" }}>
                          <Typography variant="caption" sx={{ fontWeight: 700 }}>
                            Rule Check
                          </Typography>
                          <Chip
                            label={ruleCheckResult.is_valid ? "Valid" : "Needs changes"}
                            color={ruleCheckResult.is_valid ? "success" : "default"}
                            size="small"
                            sx={ruleCheckResult.is_valid ? undefined : issueChipSx}
                          />
                          <Chip
                            label={`${ruleIssueCounts.issues} issues`}
                            size="small"
                            sx={ruleIssueCounts.issues ? issueChipSx : undefined}
                          />
                          <Chip
                            label={`${ruleIssueCounts.warnings} warnings`}
                            color={ruleIssueCounts.warnings ? "warning" : "default"}
                            size="small"
                          />
                        </Stack>
                        <Button
                          size="small"
                          onClick={() =>
                            setExpandedRuleMessageId((current) =>
                              current === message.id ? null : message.id,
                            )
                          }
                        >
                          {isRuleExpanded ? "Hide details" : "Show details"}
                        </Button>
                      </Stack>
                      <Collapse in={isRuleExpanded} timeout="auto" unmountOnExit>
                        <Box sx={{ mt: 1 }}>
                          <RuleCheckPanel result={ruleCheckResult} compact />
                        </Box>
                      </Collapse>
                    </Box>
                  )}
                </Paper>
              </Box>
            );
          })}

          {isLoading && (
            <Stack direction="row" spacing={1} sx={{ alignItems: "center", color: "text.secondary" }}>
              <CircularProgress size={18} />
              <Typography variant="body2">Waiting for response</Typography>
            </Stack>
          )}
        </Stack>
      </Box>

      <Box
        component="form"
        onSubmit={(event) => {
          event.preventDefault();
          void handleSubmit();
        }}
        sx={{
          flexShrink: 0,
          borderTop: 1,
          borderColor: "divider",
          bgcolor: "background.paper",
          px: { xs: 1.5, md: 3 },
          py: 1.5,
        }}
      >
        <Stack direction="row" spacing={1} sx={{ alignItems: "flex-end" }}>
          <TranscriptUpload
            ensureSession={ensureSession}
            onUploaded={handleTranscriptUploaded}
            onError={showError}
            disabled={isLoading || quotaExhausted}
          />
          <TextField
            fullWidth
            multiline
            minRows={1}
            maxRows={5}
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder={
              quotaExhausted
                ? usage
                  ? `Daily limit reached — resets at ${formatResetTime(usage.reset_at)}`
                  : "Daily limit reached"
                : "Message or upload a transcript PDF"
            }
            disabled={isLoading || quotaExhausted}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                void handleSubmit();
              }
            }}
          />
          <Tooltip title="Send">
            <span>
              <IconButton
                type="submit"
                color="primary"
                disabled={!canSend}
                aria-label="Send message"
                sx={{ width: 48, height: 48 }}
              >
                <SendOutlinedIcon />
              </IconButton>
            </span>
          </Tooltip>
        </Stack>
        {quotaExhausted && (
          <Stack
            direction="row"
            spacing={1}
            sx={{ alignItems: "center", justifyContent: "center", flexWrap: "wrap", mt: 1 }}
          >
            <Typography variant="body2" sx={{ color: "text.secondary" }}>
              Want to keep going today?
            </Typography>
            <Button size="small" startIcon={<ContentCopyIcon />} onClick={onContinueElsewhere}>
              Continue in your own AI assistant
            </Button>
          </Stack>
        )}
      </Box>
      <ChatErrorDialog
        open={errorDialogOpen}
        message={error ?? DEFAULT_CHAT_ERROR_MESSAGE}
        onClose={() => {
          setErrorDialogOpen(false);
          setError(null);
        }}
      />
    </Box>
  );
}
