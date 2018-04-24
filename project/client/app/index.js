import React from "react";
import App from "App";
import { render } from "react-dom";

const renderApp = () => {
  render(<App />, document.getElementById("react-app-mount"));
};

renderApp();

if (module.hot) {
  module.hot.accept("./App.js", function() {
    renderApp();
  });
}
