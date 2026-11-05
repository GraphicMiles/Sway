# Sway

Programmable video generation. Scenes are declared through an API, composed with
Remotion, and rendered to a file on request, so an agent or a script can build a
video without touching a timeline.

## Why it exists

Video is the one format that still needs a human in a GUI. If the content is
generated, the video should be generated too: the same scene graph, re-rendered
when the data changes, with an agent able to add a scene and ask for the render.
Sway is the smallest version of that idea: a scene API, a render endpoint and a
client an agent can call.

## What you can do

- **Create a scene** with a name, a component and its props.
- **List and delete scenes**, so a sequence can be assembled and edited.
- **Upload assets** and reference them from scenes.
- **Render a composition** to an MP4 on the server.
- **Drive it from an agent.** `agent.js` is a small client with `status`,
  `create` and `render` commands.
- **Check status** before a render, since rendering is the expensive step.

## Running it

Deploy, or run locally with Node and a Remotion setup:

```bash
npm install
node src/server.js
```

The API:

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | health check |
| `/status` | GET | system status |
| `/api/scenes` | GET | list scenes |
| `/api/scenes` | POST | create a scene |
| `/api/scenes/:name` | DELETE | delete a scene |
| `/api/render` | POST | render a composition |
| `/api/assets` | GET | list assets |
| `/api/assets` | POST | upload an asset |

From the client:

```bash
export SWAY_URL=https://your-sway.onrender.com
node agent.js status
node agent.js create Scene1 /assets/image.png
node agent.js render Main
```

## What is not here

- Rendering is CPU bound and synchronous per request. On a free instance a long
  composition will time out rather than finish.
- There is no editor, no preview UI and no timeline. The scene API is the
  product.
- Scenes are stored on the server's disk, so they do not survive a rebuild of the
  instance.
- The `kaggle/` and `render-ayipada*.py` files are experiment scripts used while
  building the pilot videos, not part of the service.

## How it is built

```
src/server.js       Express API: scenes, assets, render
src/index.ts        Remotion entry
src/Root.tsx        composition root
src/scenes/         scene components
public/, assets/    static files and media
out/                rendered videos
agent.js            the agent client
.render.yaml        Render blueprint
```

### Deploy

`.render.yaml` is read automatically by Render when the repository is connected.
`Procfile` is there for a plain process host.

## Licence

No licence file is included in this repository.
