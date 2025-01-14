import { Refine } from "@refinedev/core";
import { RefineKbar, RefineKbarProvider } from "@refinedev/kbar";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";

import { ErrorComponent } from "@refinedev/antd";
import "@refinedev/antd/dist/reset.css";

import {
  FileOutlined,
  HighlightOutlined,
  HomeOutlined,
  QuestionOutlined,
  NodeIndexOutlined,
  ToolOutlined,
  UserOutlined,
} from "@ant-design/icons";
import loadable from "@loadable/component";
import routerBindings, { DocumentTitleHandler, UnsavedChangesNotifier } from "@refinedev/react-router-v6";
import { ConfigProvider } from "antd";
import { Locale } from "antd/es/locale";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { BrowserRouter, Outlet, Route, Routes } from "react-router-dom";
import dataProvider from "./components/dataProvider";
import { Favicon } from "./components/favicon";
import { SpoolmanLayout } from "./components/layout";
// import liveProvider from "./components/liveProvider";
import SpoolmanNotificationProvider from "./components/notificationProvider";
import { ColorModeContextProvider } from "./contexts/color-mode";
import { languages } from "./i18n";
import { getAPIURL, getBasePath } from "./utils/url";

interface ResourcePageProps {
  resource: "printers" | "filaments";
  page: "list" | "create" | "edit" | "show";
  mode?: "create" | "clone";
}

const LoadableResourcePage = loadable(
  (props: ResourcePageProps) => import(`./pages/${props.resource}/${props.page}.tsx`),
  {
    fallback: <div>Page is Loading...</div>,
    cacheKey: (props: ResourcePageProps) => `${props.resource}-${props.page}-${props.mode ?? ""}`,
  }
);

interface LoadablePageProps {
  name: string;
}

const LoadablePage = loadable((props: LoadablePageProps) => import(`./pages/${props.name}/index.tsx`), {
  fallback: <div>Page is Loading...</div>,
  cacheKey: (props: LoadablePageProps) => `page-${props.name}`,
});

function App() {
  const { t, i18n } = useTranslation();

  const i18nProvider = {
    translate: (key: string, params?: never) => t(key, params),
    changeLocale: (lang: string) => i18n.changeLanguage(lang),
    getLocale: () => i18n.language,
  };

  // Fetch the antd locale using dynamic imports
  const [antdLocale, setAntdLocale] = useState<Locale | undefined>();
  useEffect(() => {
    const fetchLocale = async () => {
      const locale = await import(
        `./../node_modules/antd/es/locale/${languages[i18n.language].fullCode.replace("-", "_")}.js`
      );
      setAntdLocale(locale.default);
    };
    fetchLocale().catch(console.error);
  }, [i18n.language]);

  if (!import.meta.env.VITE_APIURL) {
    return (
      <>
        <h1>Missing API URL</h1>
        <p>
          App was built without an API URL. Please set the VITE_APIURL environment variable to the URL of your Spoolman
          API.
        </p>
      </>
    );
  }

  return (
    <BrowserRouter basename={getBasePath() + "/"}>
      <RefineKbarProvider>
        <ColorModeContextProvider>
          <ConfigProvider
            locale={antdLocale}
            theme={{
              token: {
                colorPrimary: "#dc7734",
              },
            }}
          >
            <Refine
              dataProvider={dataProvider(getAPIURL())}
              notificationProvider={SpoolmanNotificationProvider}
              i18nProvider={i18nProvider}
              routerProvider={routerBindings}
              resources={[
                {
                  name: "home",
                  list: "/",
                  meta: {
                    canDelete: false,
                    icon: <HomeOutlined />,
                  },
                },
                {
                  name: "printer",
                  list: "/printer",
                  show: "/printer/show/:id",
                  meta: {
                    canDelete: false,
                    icon: <NodeIndexOutlined />,
                  },
                },
                {
                  name: "help",
                  list: "/help",
                  meta: {
                    canDelete: false,
                    icon: <QuestionOutlined />,
                  },
                },
              ]}
              options={{
                syncWithLocation: true,
                warnWhenUnsavedChanges: true,
                disableTelemetry: true,
              }}
            >
              <Routes>
                <Route
                  element={
                    <SpoolmanLayout>
                      <Outlet />
                    </SpoolmanLayout>
                  }
                >
                  <Route index element={<LoadablePage name="home" />} />
                  <Route path="/printer">
                    <Route index element={<LoadableResourcePage resource="printers" page="list" />} />
                    <Route path="show/:id" element={<LoadableResourcePage resource="printers" page="show" />} />
                  </Route>
                  <Route path="/help" element={<LoadablePage name="help" />} />
                  <Route path="*" element={<ErrorComponent />} />
                </Route>
              </Routes>

              <RefineKbar />
              <UnsavedChangesNotifier />
              <DocumentTitleHandler />
              <ReactQueryDevtools />
              <Favicon url={getBasePath() + "/favicon.svg"} />
            </Refine>
          </ConfigProvider>
        </ColorModeContextProvider>
      </RefineKbarProvider>
    </BrowserRouter>
  );
}

export default App;
