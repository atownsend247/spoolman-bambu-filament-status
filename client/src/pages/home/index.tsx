import { FileOutlined, HighlightOutlined, NodeIndexOutlined, PlusOutlined, UnorderedListOutlined, UserOutlined } from "@ant-design/icons";
import { IResourceComponentsProps, useList, useTranslate } from "@refinedev/core";
import { Card, Col, Row, Statistic, theme } from "antd";
import { Content } from "antd/es/layout/layout";
import Title from "antd/es/typography/Title";
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import React, { ReactNode } from "react";
import { Link } from "react-router-dom";
import Logo from "../../icon.svg?react";
import { IPrinter } from "../printers/model";

dayjs.extend(utc);

const { useToken } = theme;

export const Home: React.FC<IResourceComponentsProps> = () => {
  const { token } = useToken();
  const t = useTranslate();

  const printers = useList<IPrinter>({
    resource: "printer",
    pagination: { pageSize: 1 },
  });

  const hasPrinters = !printers.data || printers.data.data.length > 0;

  const ResourceStatsCard = (props: { loading: boolean; value: number; resource: string; icon: ReactNode }) => (
    <Col xs={12} md={6}>
      <Card
        loading={props.loading}
        actions={[
          <Link to={`/${props.resource}`}>
            <UnorderedListOutlined />
          </Link>,
          // Disable create as read-only interface
          // <Link to={`/${props.resource}/create`}>
          //   <PlusOutlined />
          // </Link>,
        ]}
      >
        <Statistic title={t(`${props.resource}.${props.resource}`)} value={props.value} prefix={props.icon} />
      </Card>
    </Col>
  );

  return (
    <Content
      style={{
        padding: "2em 20px",
        minHeight: 280,
        maxWidth: 800,
        margin: "0 auto",
        backgroundColor: token.colorBgContainer,
        borderRadius: token.borderRadiusLG,
        color: token.colorText,
        fontFamily: token.fontFamily,
        fontSize: token.fontSizeLG,
        lineHeight: 1.5,
      }}
    >
      <Title
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: token.fontSizeHeading1,
        }}
      >
        <div
          style={{
            display: "inline-block",
            height: "1.5em",
            marginRight: "0.5em",
          }}
        >
          <Logo />
        </div>
        Spoolman Bambu Filament Status
      </Title>
      <Row justify="center" gutter={[16, 16]} style={{ marginTop: "3em" }}>
        <ResourceStatsCard
          resource="printer"
          value={printers.data?.total || 0}
          loading={printers.isLoading}
          icon={<NodeIndexOutlined />}
        />
      </Row>
      {!hasPrinters && (
        <>
          <p style={{ marginTop: 32 }}>Welcome to your Spoolman instance!</p>
          <p>
            It looks like you haven't configured any printers yet. See the <Link to="/help">Help page</Link> for help getting
            started.
          </p>
        </>
      )}
    </Content>
  );
};

export default Home;
