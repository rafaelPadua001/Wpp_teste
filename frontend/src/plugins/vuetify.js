import "vuetify/styles";
import "@mdi/font/css/materialdesignicons.css";
import { createVuetify } from "vuetify";

const vuetify = createVuetify({
  theme: {
    defaultTheme: "darkSaas",
    themes: {
      darkSaas: {
        dark: true,
        colors: {
          background: "#0f172a",
          surface: "#111827",
          "surface-bright": "#172033",
          primary: "#2563eb",
          secondary: "#38bdf8",
          error: "#ef4444",
          success: "#22c55e",
          warning: "#f59e0b",
          info: "#60a5fa",
          "on-background": "#e5e7eb",
          "on-surface": "#e5e7eb",
        },
      },
    },
  },
  defaults: {
    VCard: {
      rounded: "xl",
      elevation: 0,
    },
    VTextField: {
      variant: "outlined",
      density: "comfortable",
      color: "primary",
    },
    VTextarea: {
      variant: "outlined",
      density: "comfortable",
      color: "primary",
    },
    VBtn: {
      rounded: "xl",
    },
  },
});

export default vuetify;
