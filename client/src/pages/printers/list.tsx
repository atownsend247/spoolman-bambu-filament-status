import {
    EditOutlined,
    EyeOutlined,
    FilterOutlined,
    InboxOutlined,
    PlusSquareOutlined,
    PrinterOutlined,
    ToolOutlined,
    ToTopOutlined,
  } from "@ant-design/icons";
  import { List, useTable } from "@refinedev/antd";
  import { IResourceComponentsProps, useInvalidate, useNavigation, useTranslate } from "@refinedev/core";
  import { Button, Dropdown, Modal, Table } from "antd";
  import dayjs from "dayjs";
  import utc from "dayjs/plugin/utc";
  import { useCallback, useMemo, useState } from "react";
  import { useNavigate } from "react-router-dom";
  import {
    Action,
    ActionsColumn,
    CustomFieldColumn,
    DateColumn,
    FilteredQueryColumn,
    NumberColumn,
    RichColumn,
    SortedColumn,
    SpoolIconColumn,
  } from "../../components/column";
  import {
    useSpoolmanLocations
  } from "../../components/otherModels";
  import { useLiveify } from "../../components/liveify";
  import { removeUndefined } from "../../utils/filtering";
  import { EntityType, useGetFields } from "../../utils/queryFields";
  import { TableState, useInitialTableState, useSavedState, useStoreInitialState } from "../../utils/saveload";
  import { IPrinter } from "./model";
  
  dayjs.extend(utc);
  
  const { confirm } = Modal;
  
  interface IPrinterCollapsed extends IPrinter {

  }
  
  function translateColumnI18nKey(columnName: string): string {
    columnName = columnName.replace(".", "_");
    return `printer.fields.${columnName}`;
  }
  
  const namespace = "printerList-v2";
  
  const allColumns: (keyof IPrinterCollapsed & string)[] = [
    "id",
    "printer_id",
    "printer_ip",
    "status",
    "ams_unit_count",
    "last_mqtt_message",
    "last_mqtt_ams_message",
  ];
  const defaultColumns = allColumns.filter(
    (column_id) => ["printer_ip", "status"].indexOf(column_id) === -1
  );

  function collapseSpool(element: IPrinter): IPrinterCollapsed {   
    return {
      ...element
    };
  }
  
  export const PrinterList: React.FC<IResourceComponentsProps> = () => {
    const t = useTranslate();
    const invalidate = useInvalidate();
    const navigate = useNavigate();
    // const extraFields = useGetFields(EntityType.printer);
  
    const allColumnsWithExtraFields = [...allColumns, ...[]];
  
    // Load initial state
    const initialState = useInitialTableState(namespace);
  
    // State for the switch to show archived spools
    const [showArchived, setShowArchived] = useSavedState("printerList-showArchived", false);
  
    // Fetch data from the API
    // To provide the live updates, we use a custom solution (useLiveify) instead of the built-in refine "liveMode" feature.
    // This is because the built-in feature does not call the liveProvider subscriber with a list of IDs, but instead
    // calls it with a list of filters, sorters, etc. This means the server-side has to support this, which is quite hard.
    const { tableProps, sorters, setSorters, filters, setFilters, current, pageSize, setCurrent } =
      useTable<IPrinterCollapsed>({
        meta: {
          queryParams: {},
        },
        syncWithLocation: false,
        pagination: {
          mode: "server",
          current: initialState.pagination.current,
          pageSize: initialState.pagination.pageSize,
        },
        sorters: {
          mode: "server",
          initial: initialState.sorters,
        },
        filters: {
          mode: "server",
          initial: initialState.filters,
        },
        liveMode: "manual",
        onLiveEvent(event) {
          if (event.type === "created" || event.type === "deleted") {
            // updated is handled by the liveify
            invalidate({
              resource: "printer",
              invalidates: ["list"],
            });
          }
        },
        queryOptions: {
          select(data) {
            return {
              total: data.total,
              data: data.data,
            };
          },
        },
      });
  
    // Create state for the columns to show
    const [showColumns, setShowColumns] = useState<string[]>(initialState.showColumns ?? defaultColumns);
  
    // Store state in local storage
    const tableState: TableState = {
      sorters,
      filters,
      pagination: { current, pageSize },
      showColumns,
    };
    useStoreInitialState(namespace, tableState);
  
    // Collapse the dataSource to a mutable list
    const queryDataSource: IPrinterCollapsed[] = useMemo(
      () => (tableProps.dataSource || []).map((record) => ({ ...record })),
      [tableProps.dataSource]
    );
    const dataSource = useLiveify("printer", queryDataSource, collapseSpool);
    // const dataSource = queryDataSource;

    if (tableProps.pagination) {
      tableProps.pagination.showSizeChanger = true;
    }
  
    const { showUrl } = useNavigation();
    const actions = useCallback(
      (record: IPrinterCollapsed) => {
        const actions: Action[] = [
          { name: t("buttons.show"), icon: <EyeOutlined />, link: showUrl("printer", record.id) }
        ];
        return actions;
      },
      [t, showUrl]
    );
  
    const originalOnChange = tableProps.onChange;
    tableProps.onChange = (pagination, filters, sorter, extra) => {
      originalOnChange?.(pagination, filters, sorter, extra);
    };
  
    const commonProps = {
      t,
      navigate,
      actions,
      dataSource,
      tableState,
      sorter: true,
    };
  
    return (
      <List
        headerButtons={({ defaultButtons }) => (
          <>
            <Button
              type="primary"
              icon={<FilterOutlined />}
              onClick={() => {
                setFilters([], "replace");
                setSorters([{ field: "id", order: "asc" }]);
                setCurrent(1);
              }}
            >
              {t("buttons.clearFilters")}
            </Button>
            <Dropdown
              trigger={["click"]}
              menu={{
                items: allColumnsWithExtraFields.map((column_id) => {
                  return {
                    key: column_id,
                    label: t(translateColumnI18nKey(column_id)),
                  };
                }),
                selectedKeys: showColumns,
                selectable: true,
                multiple: true,
                onDeselect: (keys) => {
                  setShowColumns(keys.selectedKeys);
                },
                onSelect: (keys) => {
                  setShowColumns(keys.selectedKeys);
                },
              }}
            >
              <Button type="primary" icon={<EditOutlined />}>
                {t("buttons.hideColumns")}
              </Button>
            </Dropdown>
            {defaultButtons}
          </>
        )}
      >
        
        <Table
          {...tableProps}
          sticky
          tableLayout="auto"
          scroll={{ x: "max-content" }}
          dataSource={dataSource}
          rowKey="id"
          columns={removeUndefined([
            SortedColumn({
              ...commonProps,
              id: "id",
              i18ncat: "printer",
              width: 70,
            }),
            SortedColumn({
              ...commonProps,
              id: "printer_id",
              i18ncat: "printer",
              width: 70,
            }),
            SortedColumn({
              ...commonProps,
              id: "printer_ip",
              i18ncat: "printer",
              width: 70,
            }),
            SortedColumn({
              ...commonProps,
              id: "status",
              i18ncat: "printer",
              width: 70,
            }),
            DateColumn({
              ...commonProps,
              id: "last_mqtt_message",
              i18ncat: "printer",
              width: 90,
            }),
            DateColumn({
              ...commonProps,
              id: "last_mqtt_ams_message",
              i18ncat: "printer",
              width: 90,
            }),
            SortedColumn({
              ...commonProps,
              id: "ams_unit_count",
              i18ncat: "printer",
              width: 70,
            }),
            ActionsColumn(t("table.actions"), actions),
          ])}
        />
      </List>
    );
  };
  
  export default PrinterList;