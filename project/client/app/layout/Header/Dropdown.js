import React from "react";
import styled from "styled-components";
import Logo from "public/images/logo-pan-bg.png";
import MMLogo from "public/images/MM-logo.png";

export default class Dropdown extends React.Component {
  constructor() {
    super();

    this.state = {
      isActive: false
    };
  }

  render() {
    const isActive = this.state.isActive;
    return (
      <Root onClick={() => this.setState({ isActive: !isActive })}>
        <BrandArea>
          <p>Safe Networking</p>
          <BrandAreaArrow className={isActive && "active"}>
            <i className="fa fa-chevron-down" />
          </BrandAreaArrow>
        </BrandArea>
        <DropdownDrawer
          isActive={isActive}
          className={isActive ? "active" : null}
        >
          <section>
            <h3> Palo Alto Network Applications</h3>
            <Menu>
              <li>
                <a href="https://autofocus.paloaltonetworks.com" target="_blank">
                  AutoFocus
                </a>
              </li>
            </Menu>
          </section>
          <section>
            <h3>Extensions</h3>
            <Menu>
              <li>
                <IconLink href="https://live.paloaltonetworks.com/t5/MineMeld/ct-p/MineMeld" target="_blank">
                  <img src={MMLogo} />
                  <span>MineMeld</span>
                </IconLink>
              </li>
            </Menu>
          </section>
        </DropdownDrawer>
      </Root>
    );
  }
}

const IconLink = styled.a`
  display: flex !important;
  justify-content: flex-start;
  align-items: center;

  img {
    width: 30px;
    height: 30px;
  }

  span {
    display: inline-block;
    margin-left: 10px;
  }
`;

const Menu = styled.ul`
  li {
    list-style: none;

    a {
      display: block;
      padding: 7px;
      font-size: 13px;
      color: #666;
      text-decoration: none;

      &:hover {
        background: #ddd;
      }
    }
  }
`;

const BrandArea = styled.div`
  width: 100%;
  height: 100%;
  position: relative;

  &:before {
    content: " ";
    display: block;
    background: url(${Logo}) no-repeat 20px center;
    background-size: 66px;
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    opacity: 0.25;
  }

  p {
    font-size: 16px;
    font-weight: 600;
    text-transform: uppercase;
    color: #fff;
    line-height: 60px;
    margin-left: 33px;
  }
`;

const BrandAreaArrow = styled.div`
  width: 12px;
  height: 12px;
  left: 205px;
  top: 50%;
  transform: translateY(-50%);
  position: absolute;
  transition: all ease 0.2s;
  opacity: 0.666;

  &.active {
    transform: translateY(-50%) rotate(180deg);
  }

  i {
    font-size: 12px;
    color: #fff;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }
`;

const DropdownDrawer = styled.div`
  padding: 12px;

  section {
    padding: 10px 0;
    border-bottom: solid 1px #ccc;

    &:last-child {
      border: 0;
    }
  }

  h3 {
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 8px;
    padding: 0 7px;
    color: rgb(41, 43, 44);
  }

  width: 300px;
  height: auto;
  background: #fff;
  box-shadow: 0px 0px 3px rgba(0, 0, 0, 0.3);
  position: absolute;
  top: 100%;
  left: 0px;
  transition: all ease 0.3s;
  transform: translateY(-100%);
  z-index: -1;

  &.active {
    transform: translateY(0%);
  }
`;

const Root = styled.div`
  height: 100%;
  width: 340px;
  display: inline-block;
  position: relative;
  background-color: #000;
  transition: all ease 0.2s;
  s &:hover {
    background-color: #222;
  }
`;
