import React, { Component } from "react";
import styled from "styled-components";
import { withRoute } from "react-router5";
import Pages from "pages";

class RouteManager extends Component {
  renderRoute() {
    const { route } = this.props;
    const getComponentToRender = name => {
      const routes = {
        [name.startsWith("dashboard")]: Pages.Dashboard,
        [name.startsWith("iot")]: Pages.IOT,
        [name.startsWith("domain")]: Pages.Domain,
        [name.startsWith("faq")]: Pages.FAQ,
        [name.startsWith("admin")]: Pages.Admin
      };

      return routes[true];
    };

    const ComponentToRender = getComponentToRender(route.name);

    return <ComponentToRender route={route} key={this.props.route.name} />;
  }

  render() {
    return <Root>{this.renderRoute()}</Root>;
  }
}

const Root = styled.div`
  width: 100%;
  padding-top: 55px;
  height: 100%;
  flex: 1 1 100%;

  iframe {
    width: 100%;
    height: 100%;
  }
`;

export default withRoute(RouteManager);
