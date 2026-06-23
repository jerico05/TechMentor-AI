"use client";

import { Check, ChevronDown, Loader2, Search, type LucideIcon } from "lucide-react";
import * as React from "react";
import { createPortal } from "react-dom";

import { cn } from "@/lib/utils";

export interface SelectOption<T extends string | number = string | number> {
  value: T;
  label: string;
  description?: string;
  icon?: LucideIcon;
  group?: string;
  badge?: string;
}

export interface ModernSelectProps<T extends string | number = string | number> {
  id?: string;
  value: T | null | undefined;
  onChange: (value: T) => void;
  options: SelectOption<T>[];
  placeholder?: string;
  disabled?: boolean;
  loading?: boolean;
  searchable?: boolean;
  searchPlaceholder?: string;
  groupOrder?: readonly string[];
  className?: string;
  emptyMessage?: string;
  footer?: React.ReactNode;
}

function useClickOutside(
  refs: React.RefObject<HTMLElement | null>[],
  onClose: () => void,
  active: boolean,
) {
  React.useEffect(() => {
    if (!active) return;
    function onPointerDown(event: MouseEvent) {
      const target = event.target as Node;
      if (refs.some((ref) => ref.current?.contains(target))) return;
      onClose();
    }
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
    }
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [active, onClose, refs]);
}

function buildGroups<T extends string | number>(
  filtered: SelectOption<T>[],
  allOptions: SelectOption<T>[],
  groupOrder?: readonly string[],
) {
  const hasGroups = allOptions.some((o) => o.group);
  if (!hasGroups) {
    return filtered.length ? [{ label: null as string | null, options: filtered }] : [];
  }

  const buckets = new Map<string, SelectOption<T>[]>();
  for (const option of filtered) {
    const group = option.group ?? "Autres";
    const list = buckets.get(group) ?? [];
    list.push(option);
    buckets.set(group, list);
  }

  const ordered = (groupOrder ?? []).filter((label) => buckets.has(label));
  const remaining = [...buckets.keys()].filter((key) => !ordered.includes(key));
  const order = [...ordered, ...remaining];

  return order.map((label) => ({ label, options: buckets.get(label)! }));
}

export function ModernSelect<T extends string | number>({
  id,
  value,
  onChange,
  options,
  placeholder = "Sélectionner…",
  disabled = false,
  loading = false,
  searchable = false,
  searchPlaceholder = "Rechercher…",
  groupOrder,
  className,
  emptyMessage = "Aucune option trouvée.",
  footer,
}: ModernSelectProps<T>) {
  const [open, setOpen] = React.useState(false);
  const [query, setQuery] = React.useState("");
  const [panelStyle, setPanelStyle] = React.useState<React.CSSProperties>({});
  const [mounted, setMounted] = React.useState(false);
  const rootRef = React.useRef<HTMLDivElement>(null);
  const panelRef = React.useRef<HTMLDivElement>(null);

  const close = React.useCallback(() => setOpen(false), []);

  React.useEffect(() => setMounted(true), []);

  useClickOutside([rootRef, panelRef], close, open);

  const updatePanelPosition = React.useCallback(() => {
    if (!rootRef.current) return;
    const rect = rootRef.current.getBoundingClientRect();
    const viewportPadding = 12;
    const maxHeight = Math.min(360, window.innerHeight - rect.bottom - viewportPadding - 16);
    setPanelStyle({
      position: "fixed",
      top: rect.bottom + 8,
      left: rect.left,
      width: rect.width,
      zIndex: 9999,
      maxHeight: Math.max(maxHeight, 200),
    });
  }, []);

  React.useLayoutEffect(() => {
    if (!open) return;
    updatePanelPosition();
    window.addEventListener("resize", updatePanelPosition);
    window.addEventListener("scroll", updatePanelPosition, true);
    return () => {
      window.removeEventListener("resize", updatePanelPosition);
      window.removeEventListener("scroll", updatePanelPosition, true);
    };
  }, [open, updatePanelPosition]);

  const selected = options.find((o) => o.value === value) ?? null;
  const SelectedIcon = selected?.icon ?? null;

  const filtered = React.useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return options;
    return options.filter(
      (o) =>
        o.label.toLowerCase().includes(q) ||
        (o.description?.toLowerCase().includes(q) ?? false) ||
        (o.group?.toLowerCase().includes(q) ?? false),
    );
  }, [options, query]);

  const grouped = React.useMemo(
    () => buildGroups(filtered, options, groupOrder),
    [filtered, groupOrder, options],
  );

  const showSearch = searchable && options.length > 5;

  function pick(optionValue: T) {
    onChange(optionValue);
    setOpen(false);
    setQuery("");
  }

  const panel = open && mounted ? (
    <div
      ref={panelRef}
      role="listbox"
      style={panelStyle}
      className="flex flex-col overflow-hidden rounded-[1.5rem] border border-border/80 bg-white shadow-[0_16px_48px_rgba(26,43,75,0.14)]"
    >
      {showSearch ? (
        <div className="shrink-0 border-b border-border/60 p-3">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={searchPlaceholder}
              className="h-10 w-full rounded-full border border-input bg-secondary/40 pl-9 pr-4 text-sm outline-none transition focus:border-primary/40 focus:bg-white focus:ring-4 focus:ring-primary/10"
              autoFocus
            />
          </div>
        </div>
      ) : null}

      <div className="min-h-0 flex-1 overflow-y-auto p-2 scrollbar-thin">
        {loading ? (
          <div className="flex items-center justify-center gap-2 px-3 py-8 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Chargement…
          </div>
        ) : grouped.length === 0 ? (
          <p className="px-3 py-6 text-center text-sm text-muted-foreground">{emptyMessage}</p>
        ) : (
          grouped.map((group) => (
            <div key={group.label ?? "default"} className="mb-1">
              {group.label ? (
                <p className="px-3 py-2 text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
                  {group.label}
                </p>
              ) : null}
              <ul className="space-y-0.5">
                {group.options.map((option) => {
                  const Icon = option.icon;
                  const isSelected = option.value === value;
                  return (
                    <li key={String(option.value)}>
                      <button
                        type="button"
                        role="option"
                        aria-selected={isSelected}
                        onClick={() => pick(option.value)}
                        className={cn(
                          "flex w-full items-center gap-3 rounded-2xl px-3 py-2.5 text-left transition-colors",
                          isSelected ? "bg-primary/10 text-foreground" : "hover:bg-secondary/70",
                        )}
                      >
                        {Icon ? (
                          <span
                            className={cn(
                              "flex h-9 w-9 shrink-0 items-center justify-center rounded-xl",
                              isSelected ? "bg-primary text-white" : "bg-secondary text-primary",
                            )}
                          >
                            <Icon className="h-4 w-4" />
                          </span>
                        ) : null}
                        <span className="min-w-0 flex-1">
                          <span className="flex items-center gap-2">
                            <span className="truncate font-medium">{option.label}</span>
                            {option.badge ? (
                              <span className="inline-flex shrink-0 rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-semibold text-amber-700">
                                {option.badge}
                              </span>
                            ) : null}
                          </span>
                          {option.description ? (
                            <span className="mt-0.5 block truncate text-xs text-muted-foreground">
                              {option.description}
                            </span>
                          ) : null}
                        </span>
                        {isSelected ? <Check className="h-4 w-4 shrink-0 text-primary" /> : null}
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))
        )}
      </div>

      {footer ? (
        <div className="shrink-0 border-t border-border/60 px-4 py-2 text-center text-xs text-muted-foreground">
          {footer}
        </div>
      ) : null}
    </div>
  ) : null;

  return (
    <div ref={rootRef} className={cn("relative", className)}>
      <button
        id={id}
        type="button"
        disabled={disabled || loading}
        aria-haspopup="listbox"
        aria-expanded={open}
        onClick={() => setOpen((prev) => !prev)}
        className={cn(
          "input-modern flex h-12 w-full items-center justify-between gap-3 px-4 text-left",
          open && "border-primary/40 bg-white ring-4 ring-primary/10",
          (disabled || loading) && "pointer-events-none opacity-50",
        )}
      >
        <span className="flex min-w-0 flex-1 items-center gap-3">
          {loading ? (
            <span className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Chargement des métiers…
            </span>
          ) : selected ? (
            <>
              {SelectedIcon ? (
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                  <SelectedIcon className="h-4 w-4" />
                </span>
              ) : null}
              <span className="min-w-0">
                <span className="block truncate font-medium text-foreground">{selected.label}</span>
                {selected.description ? (
                  <span className="block truncate text-xs text-muted-foreground">{selected.description}</span>
                ) : null}
              </span>
            </>
          ) : (
            <span className="truncate text-muted-foreground">{placeholder}</span>
          )}
        </span>
        <ChevronDown
          className={cn("h-4 w-4 shrink-0 text-muted-foreground transition-transform", open && "rotate-180")}
        />
      </button>

      {panel && createPortal(panel, document.body)}
    </div>
  );
}
