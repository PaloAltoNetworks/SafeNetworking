import React from "react";
import styled from "styled-components";

const UtilityBar = () => (
  <Root>
    <UtilityButton title="Search" icon="search" />
    <UtilityButton title="Settings" icon="cog" />
    <UtilityButton title="FAQ" icon="question-circle" />
  </Root>
);

const UtilityButton = props => (
  <UtilityButtonRoot
    href={props.link}
    className={`utility-button fa fa-${props.icon}`}
  >
    <span className="tooltip">{props.title}</span>
  </UtilityButtonRoot>
);

const Root = styled.div`
  height: 100%;
  width: auto;
  margin-left: auto;
`;

const UtilityButtonRoot = styled.a`
  height: 100%;
  width: 60px;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  color: #fff;
  position: relative;

  &:hover {
    background: rgba(0, 0, 0, 0.2);
  }
  &:hover span {
    opacity: 1;
    visiblity: visible;
    transform: translateY(0);
  }
  span {
    position: absolute;
    top: 110%;
    background: #000;
    border-radius: 4px;
    font-weight: 500;
    padding: 0px 10px;
    height: 22px;
    line-height: 22px;
    font-size: 12px;
    transition: all ease 0.3s;
    opacity: 0;
    visiblity: hidden;
    transform: translateY(20%);
    font-family: "helvetica";
  }
  span:before {
    content: "";
    display: block;
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: solid 6px transparent;
    border-bottom: solid 6px #000;
  }
`;

export default UtilityBar;
