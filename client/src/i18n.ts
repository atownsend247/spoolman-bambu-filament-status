import dayjs from "dayjs";
import i18n from "i18next";
import detector from "i18next-browser-languagedetector";
import Backend from "i18next-http-backend";
import { initReactI18next } from "react-i18next";
import { getBasePath } from "./utils/url";

interface Language {
  name: string;
  countryCode: string;
  fullCode: string;
  djs: () => Promise<ILocale>;
}

/**
 * List of languages to load
 * The key of each object is the folder name in the locales dir.
 * name: Name of the language in the list
 * countryCode: Country code of the country's flag to display for this language
 * fullCode: Full language code, used for Ant Design's locale
 * djs: Function to load the dayjs locale, see https://github.com/iamkun/dayjs/tree/dev/src/locale for list of locales
 */
export const languages: { [key: string]: Language } = {
  ["en"]: {
    name: "English",
    countryCode: "gb",
    fullCode: "en-GB",
    djs: () => import("dayjs/locale/en"),
  },
};

i18n
  .use(Backend)
  .use(detector)
  .use(initReactI18next)
  .init({
    supportedLngs: Object.keys(languages),
    backend: {
      loadPath: getBasePath() + "/locales/{{lng}}/{{ns}}.json",
    },
    ns: "common",
    defaultNS: "common",
    fallbackLng: "en",
  });

i18n.on("languageChanged", function (lng) {
  languages[lng].djs().then((djs) => dayjs.locale(djs.name));
});

export default i18n;
