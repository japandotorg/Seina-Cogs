import { defineConfig } from "astro/config";

import starlight from "@astrojs/starlight";
import tailwind from "@astrojs/tailwind";
import icon from "astro-icon";

const AdsenseID = process.env.ADSENSE;
const MoneTag = process.env.MONETAG;


export default defineConfig({
    integrations: [starlight({
        title: 'Seina Cogs',
        head: [
            {
                tag: "meta",
                attrs: {
                    name: "google-adsense-account",
                    content: `ca-pub-${AdsenseID}`
                },
            },
            /*
             *  {
             *      tag: "meta",
             *      attrs: {
             *          name: "monetag",
             *          content: `${MoneTag}`
             *      }
             *  },
             *  {
             *      tag: "script",
             *      attrs: {
             *          src: "https://alwingulla.com/88/tag.min.js",
             *          "data-zone": "120222",
             *          "async data-cfasync": "false",
             *      }
             *  }
             */
        ],
        logo: {
            src: "./src/assets/seina.svg",
        },
        social: {
            discord: "https://discord.gg/AyMrA7KMSp",
            github: "https://github.com/japandotorg/Seina-Cogs",
        },
        customCss: [
            "./src/styles/tailwind.css",
        ],
        sidebar: [
            {
                label: "Getting Started",
                slug: "starter",
            },
            {
                label: "Tags",
                autogenerate: { directory: "tags" }
            }
        ],
    }),
    tailwind({}),
    icon()],
});