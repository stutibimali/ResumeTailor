# ResumeTailor — Frontend

The Next.js web interface for ResumeTailor. See the [main README](../README.md) for the project overview, the AI pipeline and backend setup.

## Getting started

Requires Node.js 20 or later. Run the FastAPI backend alongside it (see the main README).

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

The main page is `app/page.tsx`, and the root layout is `app/layout.tsx`. The page auto-updates as you edit.

## Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start the development server with hot reload |
| `npm run build` | Create a production build |
| `npm run start` | Serve the production build |

## Built with

- [Next.js](https://nextjs.org) (App Router), bootstrapped with `create-next-app`
- React and TypeScript
- [Geist](https://vercel.com/font) font via `next/font`
