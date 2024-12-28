import starlight from "@astrojs/starlight-tailwind";

import colors from "tailwindcss/colors";
import { type Config } from "tailwindcss";


export default <Partial<Config>>{
	content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
	theme: {
		extend: {
			colors: {
				accent: colors.yellow,
				gray: colors.zinc,
			}
		},
	},
	plugins: [starlight()],
}
