import { useQuery } from "@tanstack/react-query";
import { Tooltip } from "antd";
import { ColumnFilterItem } from "antd/es/table/interface";
import { getAPIURL } from "../utils/url";

export function useSpoolmanLocations(enabled: boolean = false) {
    return useQuery<string[]>({
      enabled: enabled,
      queryKey: ["locations"],
      queryFn: async () => {
        const response = await fetch(getAPIURL() + "/location");
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      },
      select: (data) => {
        return data.sort();
      },
    });
  }