import { InboxOutlined, PrinterOutlined, ToTopOutlined } from "@ant-design/icons";
import { DateField, NumberField, Show, TextField } from "@refinedev/antd";
import { IResourceComponentsProps, useInvalidate, useShow, useTranslate } from "@refinedev/core";
import { Button, Modal, Typography } from "antd";
import { EntityType, useGetFields } from "../../utils/queryFields";
import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import React from "react";
import { IPrinter } from "./model";

dayjs.extend(utc);

const { Title } = Typography;
const { confirm } = Modal;

export const PrinterShow: React.FC<IResourceComponentsProps> = () => {
  const t = useTranslate();
  const invalidate = useInvalidate();

  const { query } = useShow<IPrinter>({
    liveMode: "manual",
  });
  const { data, isLoading } = query;

  const record = data?.data;

  const formatTitle = (item: IPrinter) => {
    return t("printer.titles.show_title", {
      id: item.id,
      name: item.printer_id,
      interpolation: { escapeValue: false },
    });
  };

  return (
    <Show
      isLoading={isLoading}
      title={record ? formatTitle(record) : ""}
      headerButtons={({ defaultButtons }) => (
        <>
          {defaultButtons}
        </>
      )}
    >
      <Title level={5}>{t("printer.fields.id")}</Title>
      <NumberField value={record?.id ?? ""} />
      <Title level={5}>{t("printer.fields.printer_id")}</Title>
      <TextField value={record?.printer_id ?? ""} />
      <Title level={5}>{t("printer.fields.printer_ip")}</Title>
      <TextField value={record?.printer_ip ?? ""} />
      <Title level={5}>{t("printer.fields.status")}</Title>
      <TextField value={record?.status ?? ""} />
      <Title level={5}>{t("printer.fields.ams_unit_count")}</Title>
      <NumberField value={record?.ams_unit_count ?? 0} />
      <Title level={5}>{t("printer.fields.last_mqtt_message")}</Title>
      <DateField
        hidden={!record?.last_mqtt_message}
        value={dayjs.utc(record?.last_mqtt_message).local()}
        title={dayjs.utc(record?.last_mqtt_message).local().format()}
        format="YYYY-MM-DD HH:mm:ss"
      />
      <TextField 
        hidden={!!record?.last_mqtt_message}
        value={"No MQTT Update recieved yet"}
      />
      <Title level={5}>{t("printer.fields.last_mqtt_ams_message")}</Title>
      <DateField 
        hidden={!record?.last_mqtt_ams_message}
        value={dayjs.utc(record?.last_mqtt_ams_message).local()}
        title={dayjs.utc(record?.last_mqtt_ams_message).local().format()}
        format="YYYY-MM-DD HH:mm:ss"
      />
      <TextField 
        hidden={!!record?.last_mqtt_ams_message}
        value={"No MQTT AMS Update recieved yet"}
      />
    </Show>
  );
};

export default PrinterShow;