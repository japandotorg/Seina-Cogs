import { defineConfig } from "astro/config";

import starlight from "@astrojs/starlight";
import tailwind from "@astrojs/tailwind";
import icon from "astro-icon";


const AdsenseID = process.env.ADSENSE


export default defineConfig({
    integrations: [starlight({
        title: 'Seina Cogs',
        head: [
            {
                tag: "script",
                attrs: {
                    src: `<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-${AdsenseID}" crossorigin="anonymous">`
                },
            },
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