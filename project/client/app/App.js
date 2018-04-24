import React from "react";
import styled from "styled-components";
import "styles/global.css";
import Header from "layout/Header";
import router from "router";
import { RouterProvider } from "react-router5";
import RouteManager from "router/RouteManager";

const App = () => (
  <RouterProvider router={router}>
    <Root>
      <Header />
      <RouteManager />
    </Root>
  </RouterProvider>
);

const Root = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  flex-flow: column nowrap;
`;

export default App;
