import React from "react";
import { Link } from "react-router5";
import styled from "styled-components";

const Nav = () => (
  <Root>
    <ul>
      <li>
        <Link routeName="dashboard">Dashboard</Link>
      </li>
      <li>
        <Link routeName="domain">Domain</Link>
      </li>
      <li>
        <Link routeName="iot">iot</Link>
      </li>
      <li>
        <Link routeName="space"></Link>
      </li>
      <li>
        <Link routeName="space2"></Link>
      </li>
      <li>
        <Link routeName="space3"></Link>
      </li>
      <li>
        <Link routeName="space4"></Link>
      </li>
      <li>
        <Link routeName="space5"></Link>
      </li>
      <li>
        <Link routeName="space6"></Link>
      </li>
      <li>
        <Link routeName="space7"></Link>
      </li>
      <li>
        <Link routeName="space8"></Link>
      </li>
      <li>
        <Link routeName="space9"></Link>
      </li>
      <li>
        <Link routeName="space10"></Link>
      </li>
      <li>
        <Link routeName="space11"></Link>
      </li>
      <li>
        <Link routeName="space12"></Link>
      </li>
      <li>
        <Link routeName="space13"></Link>
      </li>
      <li>
        <Link routeName="space14"></Link>
      </li>
      <li>
        <Link routeName="space15"></Link>
      </li>
      <li>
        <Link routeName="space16"></Link>
      </li>
      <li>
        <Link routeName="space17"></Link>
      </li>
      <li>
        <Link routeName="space18"></Link>
      </li>
      <li>
        <Link routeName="space19"></Link>
      </li>
      <li>
        <Link routeName="space20"></Link>
      </li>
      <li>
        <Link routeName="admin">admin</Link>
      </li>
    </ul>
  </Root>
);

const Root = styled.nav`
  ul {
    display: flex;
    height: 100%;
    margin: 0;
    padding: 0;

    li {
      list-style: none;
      color: #fff;

      a {
        text-decoration: none;
        padding: 0 20px;
        height: 100%;
        display: block;
        color: #fff;
        opacity: 0.666;
        line-height: 55px;
        text-transform: uppercase;
        font-size: 13px;
        border-bottom: solid 5px transparent;

        &.active {
          border-bottom: solid 5px #0e9ac8;
          opacity: 1;
          background: rgba(0, 0, 0, 0.3);
        }

        &:hover {
          opacity: 1;
        }
      }
    }
  }
`;

export default Nav;
