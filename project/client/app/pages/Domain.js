import React, { Component } from "react";
import styled from "styled-components";
import Sidebar from "layout/Sidebar";
import Pages from "pages";

export default class Domain extends Component {
  renderContent() {
    const { route } = this.props;
    if (route.name === "domain") return <Pages.DomainDashboard />;
    if (route.name === "domain.malware-by-file") return <Pages.DomainMalByFile />;
    if (route.name === "domain.malware-resolvers") return <Pages.DomainMalResolvers />;
    if (route.name === "domain.malware-dns-resolver") return <Pages.DomainMalDNSResolver />;
    if (route.name === "domain.at-risk-clients") return <Pages.DomainAtRiskClients />;
    if (route.name === "domain.top-10-malware") return <Pages.DomainTop10Malware />;

  }
  
  render() {
    return (
      <Root>
        <Sidebar
          links={[
            {
              routeName: "domain",
              title: "Dashboard",
              icon: "tachometer"
            },
            {
              routeName: "domain.malware-by-file",
              title: "Malware by FileType",
              icon: "pie-chart"
            },
            {
              routeName: "domain.malware-resolvers",
              title: "Malware Resolvers",
              icon: "bar-chart"
            },
            {
              routeName: "domain.malware-dns-resolver",
              title: "Malware by DNS Server",
              icon: "bar-chart"
            },
            {
              routeName: "domain.at-risk-clients",
              title: "At Risk Clients",
              icon: "bar-chart"
            },
            {
              routeName: "domain.top-10-malware",
              title: "Top 10 Malware",
              icon: "bar-chart"
            }               
          ]}
        />
        {this.renderContent()}
      </Root>
    );
  }
}

const Root = styled.div`
  display: flex;
  width: 100%;
  height: 100%;
`;
