import { createTheme } from "@mui/material/styles";

import { colors } from "./colors";

const sharedPalette = {
  secondary: { main: colors.info },
  success: { main: colors.success },
  warning: { main: colors.warning },
  error: { main: colors.danger },
};

let appTheme = createTheme({
  cssVariables: { colorSchemeSelector: "data" },
  colorSchemes: {
    light: {
      palette: {
        ...sharedPalette,
        primary: {
          main: colors.fuGreen,
          dark: colors.fuGreenDark,
          light: colors.fuGreenLight,
        },
        background: { default: colors.paperMuted, paper: colors.paper },
        divider: colors.border,
        text: { primary: colors.ink, secondary: "#52615c" },
      },
    },
    dark: {
      palette: {
        ...sharedPalette,
        primary: {
          main: "#78d6b4",
          dark: colors.fuGreenDark,
          light: "#b8f1da",
          contrastText: "#10221b",
        },
        background: { default: "#111816", paper: "#17211e" },
        divider: "rgba(255, 255, 255, 0.12)",
        text: { primary: "#eef4f1", secondary: "#b8c7c1" },
      },
    },
  },
  shape: { borderRadius: 6 },
  typography: {
    fontFamily:
      'Arial, "Helvetica Neue", Helvetica, system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
    h1: { fontSize: "1.55rem", fontWeight: 700, letterSpacing: 0 },
    h2: { fontSize: "1.25rem", fontWeight: 700, letterSpacing: 0 },
    h3: { fontSize: "1rem", fontWeight: 700, letterSpacing: 0 },
    button: { textTransform: "none", fontWeight: 700, letterSpacing: 0 },
  },
});

appTheme = createTheme(appTheme, {
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        "*": {
          scrollbarColor: "#aab5b1 #f5f7f6",
          scrollbarWidth: "thin",
          "&::-webkit-scrollbar": { width: 10, height: 10 },
          "&::-webkit-scrollbar-track": { backgroundColor: colors.paperMuted },
          "&::-webkit-scrollbar-thumb": {
            backgroundColor: "#aab5b1",
            border: `2px solid ${colors.paperMuted}`,
            borderRadius: 8,
          },
          "&::-webkit-scrollbar-thumb:hover": { backgroundColor: "#87958f" },
          ...appTheme.applyStyles("dark", {
            scrollbarColor: "#52615c #111816",
            "&::-webkit-scrollbar-track": { backgroundColor: "#111816" },
            "&::-webkit-scrollbar-thumb": {
              backgroundColor: "#52615c",
              border: "2px solid #111816",
            },
            "&::-webkit-scrollbar-thumb:hover": { backgroundColor: "#6c7d77" },
          }),
        },
      },
    },
    MuiButton: { styleOverrides: { root: { borderRadius: 6 } } },
    MuiSwitch: {
      styleOverrides: {
        switchBase: {
          "&.Mui-checked": {
            color: colors.fuGreen,
            ...appTheme.applyStyles("dark", { color: "#b8f1da" }),
          },
          "&.Mui-checked + .MuiSwitch-track": {
            backgroundColor: colors.fuGreen,
            opacity: 1,
            ...appTheme.applyStyles("dark", { backgroundColor: "#43ad86" }),
          },
        },
      },
    },
    MuiCard: { styleOverrides: { root: { borderRadius: 8 } } },
    MuiChip: { styleOverrides: { root: { borderRadius: 6 } } },
    MuiTab: {
      styleOverrides: {
        root: { minHeight: 52, letterSpacing: 0, textTransform: "none" },
      },
    },
    MuiTextField: { defaultProps: { variant: "outlined" } },
  },
});

export { appTheme };
