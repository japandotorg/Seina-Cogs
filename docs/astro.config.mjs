import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

import icon from "astro-icon";
import sitemap from "@astrojs/sitemap";
import tailwind from "@astrojs/tailwind";
import starWarp from "@inox-tools/star-warp";


const ADSENSE = process.env.ADSENSE || "undefined";


/** @type {import("astro").AstroUserConfig} */
export default defineConfig({
    site: "https://cogs.melonbot.io",
    integrations: [
        sitemap(
            { xslURL: "/sitemap.xml" }
        ),
        starlight(
            {
                title: 'Seina Cogs',
                editLink: {
                    baseUrl: "https://github.com/japandotorg/Seina-Cogs/edit/main/docs"
                },
                plugins: [
                    starWarp({ path: "/find", openSearch: { enabled: true, title: "Seina-Cogs" } }),
                ],
                head: [
                    {
                        tag: "meta",
                        attrs: {
                            name: "google-adsense-account",
                            content: `ca-pub-${ADSENSE}`,
                        },
                    },
                    {
                        tag: "script",
                        attrs: {
                            "async src": `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-${ADSENSE}`,
                            crossorigin: "anonymous",
                        },
                    },
                    {
                        tag: "link",
                        attrs: {
                            rel: "sitemap",
                            href: "/sitemap-index.xml"
                        }
                    },
                    {
                        tag: "link",
                        attrs: {
                            rel: "search",
                            type: "application/opensearchdescription+xml",
                            href: "/find.xml",
                            title: "Seina Cogs",
                        },
                    }
                ],
                components: {
                    Head: "./src/components/Head.astro",
                },
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
                        autogenerate: { directory: "tags" },
                    }
                ],
            },
        ),
        tailwind(),
        icon(),
    ],
});
