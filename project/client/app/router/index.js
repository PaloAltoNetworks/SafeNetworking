import createRouter from "router5";
import browserPlugin from "router5/plugins/browser";
import listenersPlugin from "router5/plugins/listeners";
import routes from "./routes";

const router = createRouter(routes)
  .usePlugin(browserPlugin())
  .usePlugin(listenersPlugin())
  .start("/");

export default router;
