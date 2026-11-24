/** Local module v0.4; source IDs and nanoseconds remain decimal strings. */
export type DecimalString = string;
export type Team = string; // validated project slug
export interface RosterSeat {seat:string;team:Team;runtime:Runtime}
export type Activity = 'working'|'idle'|'needs-input'|'unknown';
export type Presence = 'running'|'exited'|'stopped'|'detached'|'unknown';
export type Runtime = 'claude-code'|'codex'|'pi'|'omp'|'terminal'|'stub';
export interface ModuleConfig {version:'1.1.0';project_id:string;title:string;roster:RosterSeat[];namespace:string;ttl_seconds:number;bindings:Record<string,string>}
export interface SeatObservation {node_id:string;seat:string|null;team:Team|'unmapped';runtime:Runtime|null;presence:Presence;activity:Activity;needs_input:'yes'|'no'|'unknown';sample_ns:DecimalString}
export interface Observation {kind:'metric'|'log';namespace:string;instance:string;observed_ns:DecimalString;name:string;value:DecimalString|null;data:Record<string,string>}
export interface JournalRow extends Observation {seq:number;received_ns:DecimalString}
export interface History {rows:JournalRow[];next_cursor:number;has_more:boolean}
export interface Snapshot {cursor:number;high_watermark:number;as_of_ns:DecimalString;mode:'observed'|'replay';history_completeness:'unknown';ttl_seconds:number;seats:SeatObservation[];recent:(Observation & {seq:number})[];communication_available:false}
