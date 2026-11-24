export type Runtime = "codex" | "claude-code" | "omp" | "pi" | "stub" | "terminal";
export type SeatId = `${string}.${string}`;
export interface Team { id: string; label: string; lead: string; pilot_seats: string[] }
export interface FleetSeat { team: string; seat: string; runtime: Runtime; cell: string; scope: string; role: string }
export interface Mission { id: string; owner: SeatId; reviewer: SeatId; depends_on: string[]; title: string; acceptance: string; write_paths: string[]; status: "proposed" }
export interface ProjectInit { schema_version: "1.0.0"; project_id: string; title: string; summary: string; teams: Team[]; roster: string; missions: string; briefs: string; guidance: string; context_dirs: string[]; source_repositories: ({id:string;kind:"git";url:string}|{id:string;kind:"snapshot";path:string})[]; policy: {max_seats:number;initial_seats:number;permission_policy:"builtin:standard";approval_required:true;live_execution_allowed:false;require_clean_repo:true}; sentinel: {enabled:true;ttl_seconds:number;default_port:number;exporter_commit:string;start:"latest"|"retained";poll_ms:number;seat_poll_ms:number;pseudonymize_seats:boolean} }
