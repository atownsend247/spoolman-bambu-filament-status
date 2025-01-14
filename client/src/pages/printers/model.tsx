
export enum WeightToEnter {
  used_weight = 1,
  remaining_weight = 2,
  measured_weight = 3,
}

export interface IPrinter {
  id: number;
  printer_id: string;
  printer_ip: string;
  status: string;
  ams_unit_count?: number;
  ams_active_spools_count?: number;
  last_mqtt_message?: string;
  last_mqtt_ams_message?: string;
}

// IPrinterParsedExtras is the same as IPrinter, but with the extra field parsed into its real types
export type IPrinterParsedExtras = Omit<IPrinter, "extra"> & { extra?: { [key: string]: unknown } };
