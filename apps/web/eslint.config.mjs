import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  // Override default ignores of eslint-config-next.
  globalIgnores([
    // Default ignores of eslint-config-next:
    ".next/**",
    "out/**",
    "build/**",
    "next-env.d.ts",
  ]),
  // Regras de Fronteira da Clean Architecture (Mapeamento de Círculos do Uncle Bob)
  {
    files: ["src/domain/**/*.ts", "src/domain/**/*.tsx"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["**/application/**", "@/application/**", "../application/**"],
              message: "Regra de Dependência Violada: Camada DOMAIN (Entities) NUNCA deve importar nada de APPLICATION (Use Cases)."
            },
            {
              group: ["**/infrastructure/**", "@/infrastructure/**", "../infrastructure/**"],
              message: "Regra de Dependência Violada: Camada DOMAIN (Entities) NUNCA deve importar nada de INFRASTRUCTURE (Interface Adapters / Frameworks)."
            },
            {
              group: ["**/presentation/**", "@/presentation/**", "../presentation/**"],
              message: "Regra de Dependência Violada: Camada DOMAIN (Entities) NUNCA deve importar nada de PRESENTATION (Interface Adapters / Visual)."
            }
          ]
        }
      ]
    }
  },
  {
    files: ["src/application/**/*.ts"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["**/infrastructure/**", "@/infrastructure/**", "../infrastructure/**"],
              message: "Regra de Dependência Violada: Camada APPLICATION (Use Cases) NUNCA deve importar nada de INFRASTRUCTURE (Interface Adapters / Frameworks)."
            },
            {
              group: ["**/presentation/**", "@/presentation/**", "../presentation/**"],
              message: "Regra de Dependência Violada: Camada APPLICATION (Use Cases) NUNCA deve importar nada de PRESENTATION (Interface Adapters / Visual)."
            }
          ]
        }
      ]
    }
  },
  {
    files: ["src/infrastructure/**/*.ts"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["**/presentation/**", "@/presentation/**", "../presentation/**"],
              message: "Regra de Dependência Violada: Camada INFRASTRUCTURE (Gateways) NUNCA deve importar nada de PRESENTATION (Visual)."
            }
          ]
        }
      ]
    }
  },
  {
    rules: {
      "@typescript-eslint/no-explicit-any": "off",
      "@typescript-eslint/no-unused-vars": "off",
      "react-hooks/set-state-in-effect": "off",
      "@next/next/no-html-link-for-pages": "off",
      "react/no-unescaped-entities": "off"
    }
  }
]);

export default eslintConfig;

