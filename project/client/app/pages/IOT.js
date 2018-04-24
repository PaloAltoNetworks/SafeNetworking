import React, { Component } from "react";
import styled from "styled-components";
import Sidebar from "layout/Sidebar";
import Pages from "pages";
import UC from "public/images/UnderConstruction.png";

export default class IOT extends Component {
  renderContent() {
    const { route } = this.props;
    if (route.name === "iot") return <Pages.IOTDashboard />;
    if (route.name === "iot.child-route") return <Pages.IOTChild />;
  }

  render() {
    return (
      <div>
        <img src={UC} />
      </div>
    );
  }
  // render() {
  //   return (
  //     // <Root>
  //     //   <Sidebar
  //     //     links={[
  //     //       {
  //     //         routeName: "iot",
  //     //         title: "Dashboard",
  //     //         icon: "tachometer"
  //     //       },
  //     //       {
  //     //         routeName: "iot.child-route",
  //     //         title: "Child Route",
  //     //         icon: "gear"
  //     //       }
  //     //     ]}
  //     //   />
  //     //   {this.renderContent()}
  //     // </Root>
  //   );
  // }
}

const Root = styled.div`
  display: flex;
  width: 100%;
  height: 100%;
`;
