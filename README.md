# Guild Glory — Vercel API package

This package adapts the uploaded Flask source to a Vercel Python Function.

## Endpoint

`GET /api/rishu?Tc=TEAM_CODE&Emote_id=EMOTE_ID&Target_Uid=PLAYER_UID`

Every request must include this HTTP header:

`x-api-key: YOUR_API_SECRET`

The API secret is deliberately not placed in the URL.

## Vercel Environment Variables

In Vercel: Project → Settings → Environment Variables, add:

- `BOT_UID` — game bot account UID
- `BOT_PASSWORD` — game bot account password/token used by the source
- `API_SECRET` — a long random secret used to protect the endpoint

Add them for Production (and Preview if you intend to test there), then redeploy.
Never commit real credentials to GitHub or share screenshots containing them.

## Deploy from Android

1. Extract this ZIP on your phone.
2. Create a private GitHub repository.
3. Upload the contents of this folder to the repository root (not the ZIP file itself).
4. Open https://vercel.com/new and import that repository.
5. Keep the project root as `/`; use the default Python build detection.
6. Add the three Environment Variables listed above.
7. Deploy.
8. Test the deployed endpoint with a GET request and the `x-api-key` header.

Example URL (replace the values):

`https://YOUR-PROJECT.vercel.app/api/rishu?Tc=TEAM_CODE&Emote_id=EMOTE_ID&Target_Uid=PLAYER_UID`

## Important compatibility note

The original source opens outbound raw TCP connections to game-server hosts and uses threads, queues, and timed socket operations. Vercel Python Functions are bounded, request-scoped serverless executions, not a continuously running VPS. This package is a deployment adaptation, not a guarantee that the external game-server TCP connection will be permitted or remain reliable on Vercel. After deployment, verify with Vercel Runtime Logs. If the game-server connection fails or the operation exceeds the function duration, run this API on a conventional long-running Python host instead.

The original source's local `selftest()` is not run during Vercel imports. Its earlier local assertion failure is therefore not fixed by this packaging step; test the API carefully before using it.

## Security

The uploaded source contained embedded game account credentials. This package replaces those values with environment variables. Rotate any credentials that were previously shared or committed. Keep the repository private and use the API key header for every request.
