import React, { Component } from "react";
import { Link } from "react-router5";
import styled from "styled-components";

export default class Sidebar extends Component {
  renderLinks() {
    return this.props.links.map((l,i) => (
      <li key={i}>
        <IconLink routeName={l.routeName}>
          <i className={`fa fa-${l.icon}`} />
          <span>{l.title}</span>
        </IconLink>
      </li>
    ));
  }
  render() {
    return (
      <Root>
        <ul>{this.renderLinks()}</ul>
      </Root>
    );
  }
}

const IconLink = styled(Link)`
  padding: 10px;
  font-weight: 300;
  display: block;
  color: #ccc;
  text-decoration: none;

  i {
    font-size: 18px;
  }
  span {
    margin-left: 10px;
    font-size: 14px;
  }

  &.active {
    background: #000;
  }

  &:hover {
    background: #000;
  }
`;

const Root = styled.div`
  background: #444;
  width: 200px;
  height: 100%;
  flex: 0 0 auto;
  z-index: 5;
  position: relative;
  box-shadow: 0 0 6px rgba(0, 0, 0, 0.4);

  li {
    list-style: none;
    width: 100%;
  }
`;
