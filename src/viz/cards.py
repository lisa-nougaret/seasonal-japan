import textwrap

import pandas as pd


def format_card_date(date) -> str:
    if date is None or pd.isna(date):
        return "N/A"

    date = pd.to_datetime(date)
    return date.strftime("%d<br>%b")


def format_inline_date(date) -> str:
    if date is None or pd.isna(date):
        return "N/A"

    return pd.to_datetime(date).strftime("%d %b %Y")


def format_range_compact(start_date, end_date) -> str:
    if start_date is None or end_date is None:
        return "Not available"

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    return f"{start_date.strftime('%d %b')} – {end_date.strftime('%d %b %Y')}"


_DEFAULT_FULL_BLOOM_GAP = 8  # fallback when no historical gap data exists for a station


def get_best_visit_dates(forecast_df: pd.DataFrame, full_bloom_gap_days: int | None = None) -> dict:
    if forecast_df.empty or pd.isna(forecast_df.iloc[0]["predicted_event_date"]):
        return {"available": False}

    first_bloom = pd.to_datetime(forecast_df.iloc[0]["predicted_event_date"])
    gap = full_bloom_gap_days if full_bloom_gap_days is not None else _DEFAULT_FULL_BLOOM_GAP

    full_bloom = first_bloom + pd.Timedelta(days=gap)
    peak_start = full_bloom - pd.Timedelta(days=1)
    peak_end = full_bloom + pd.Timedelta(days=1)

    visit_start = peak_start - pd.Timedelta(days=2)
    visit_end = peak_end + pd.Timedelta(days=4)

    hanafubuki_start = full_bloom + pd.Timedelta(days=3)
    hanafubuki_end = full_bloom + pd.Timedelta(days=10)

    return {
        "available": True,
        "first_bloom": first_bloom,
        "full_bloom": full_bloom,
        "peak_start": peak_start,
        "peak_end": peak_end,
        "visit_start": visit_start,
        "visit_end": visit_end,
        "hanafubuki_start": hanafubuki_start,
        "hanafubuki_end": hanafubuki_end,
    }


def _interp_bloom_color(t: float) -> str:
    """Pale pink → deep pink → dark plum along the bloom arc."""
    stops = [
        (0.00, (226, 210, 214)),
        (0.28, (224, 158, 172)),
        (0.46, (212, 108, 134)),
        (0.62, (152,  96, 108)),
        (0.80, ( 96,  68,  76)),
        (1.00, ( 50,  42,  48)),
    ]
    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        if t <= t1:
            u = (t - t0) / (t1 - t0)
            r = round(c0[0] + (c1[0] - c0[0]) * u)
            g = round(c0[1] + (c1[1] - c0[1]) * u)
            b = round(c0[2] + (c1[2] - c0[2]) * u)
            return f"rgb({r},{g},{b})"
    lc = stops[-1][1]
    return f"rgb({lc[0]},{lc[1]},{lc[2]})"


def _estimated_tag(prediction_status: str | None) -> str:
    if prediction_status != "estimated":
        return ""
    return (
        '<span style="font:500 10px/1 \'IBM Plex Mono\',monospace;letter-spacing:1px;'
        'color:#e69bb4;border:1px solid rgba(230,155,180,0.4);border-radius:20px;'
        'padding:2px 8px;margin-left:8px;vertical-align:middle;">'
        "USES CLIMATE NORMALS"
        "</span>"
    )


def _prose_paragraph(
    first_bloom,
    peak_start,
    peak_end,
    hanafubuki_end,
    forecast_doy: int | None,
    hist_avg_doy: int | None,
) -> str:
    try:
        fb_fmt = first_bloom.strftime("%-d %B")
        ps_day = peak_start.strftime("%-d")
        pe_fmt = peak_end.strftime("%-d %B")
        hf_fmt = hanafubuki_end.strftime("%-d %B")
    except ValueError:
        fb_fmt = first_bloom.strftime("%d %B").lstrip("0")
        ps_day = peak_start.strftime("%d").lstrip("0")
        pe_fmt = peak_end.strftime("%d %B").lstrip("0")
        hf_fmt = hanafubuki_end.strftime("%d %B").lstrip("0")

    peak_fmt = f"{ps_day}–{pe_fmt}"

    if forecast_doy is not None and hist_avg_doy is not None:
        delta = forecast_doy - hist_avg_doy
        if abs(delta) <= 1:
            comparison = " — roughly on par with the twenty-year average"
        elif delta < 0:
            d = abs(delta)
            comparison = f" — about {d} day{'s' if d != 1 else ''} earlier than the twenty-year average"
        else:
            comparison = f" — about {delta} day{'s' if delta != 1 else ''} later than the twenty-year average"
    else:
        comparison = ""

    return (
        f'<p style="font:300 16px/1.6 \'Newsreader\',serif;color:#cfc6d6;margin:0 0 32px;">'
        f'First light appears in the blossoms around '
        f'<em style="font-style:normal;color:#f6f1f4;">{fb_fmt}</em>, '
        f"quietly marking the season's return. "
        f'Every tree glows at its fullest from '
        f'<em style="font-style:normal;color:#ff8fa9;">{peak_fmt}</em>{comparison}. '
        f'Then loose petals fill the air in brief, luminous flurries through '
        f'<em style="font-style:normal;color:#9a8fa0;">{hf_fmt}</em>, before the season fades.'
        f'</p>'
    )


def _accuracy_footnote(mae: float | None) -> str:
    if mae is None:
        return ""
    mae_str = f"{mae:.0f}"
    if mae > 20:
        return (
            '<div style="margin-top:40px;display:flex;align-items:center;gap:11px;justify-content:flex-end;">'
            '<span style="font:600 10px/1 \'IBM Plex Mono\',monospace;letter-spacing:1px;color:#b08a6a;'
            'background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:5px;padding:5px 8px;">⚠</span>'
            '<span style="font:300 italic 13px/1.4 \'Newsreader\',serif;color:#b08a6a;">'
            'Forecast reliability is lower for this region — allow extra flexibility when planning.</span>'
            '</div>'
        )
    return (
        f'<div style="margin-top:40px;display:flex;align-items:center;gap:11px;justify-content:flex-end;">'
        f'<span style="font:600 10px/1 \'IBM Plex Mono\',monospace;letter-spacing:1px;color:#7a7488;'
        f'background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:5px;padding:5px 8px;">±{mae_str}d</span>'
        f'<span style="font:300 italic 13px/1.4 \'Newsreader\',serif;color:#6f6a80;">'
        f'Forecast accuracy — typically within {mae_str} days for this station.</span>'
        f'</div>'
    )


def render_forecast_section(
    station_name: str,
    forecast_df: pd.DataFrame,
    hist_avg_doy: int | None = None,
    full_bloom_gap_days: int | None = None,
) -> str:
    dates = get_best_visit_dates(forecast_df, full_bloom_gap_days=full_bloom_gap_days)
    if not dates["available"]:
        return ""

    first_bloom    = dates["first_bloom"]
    full_bloom     = dates["full_bloom"]
    peak_start     = dates["peak_start"]
    peak_end       = dates["peak_end"]
    visit_start    = dates["visit_start"]
    visit_end      = dates["visit_end"]
    hanafubuki_end = dates["hanafubuki_end"]

    row = forecast_df.iloc[0]
    station_mae       = float(row["station_mae_days"]) if pd.notna(row.get("station_mae_days")) else None
    global_mae        = float(row["mae_days"]) if pd.notna(row.get("mae_days")) else None
    prediction_status = str(row.get("prediction_status", "")) or None
    forecast_doy      = int(row["predicted_day_of_year"]) if pd.notna(row.get("predicted_day_of_year")) else None

    station_display = station_name.title()
    estimated_html  = _estimated_tag(prediction_status)

    n_days = (hanafubuki_end - first_bloom).days + 2
    cal_days = [first_bloom + pd.Timedelta(days=i) for i in range(n_days)]
    peak_center_idx = (full_bloom - first_bloom).days
    best_s = max(0, (visit_start - first_bloom).days)
    best_e = min(n_days - 1, (visit_end - first_bloom).days)

    cell_pct  = 100.0 / n_days
    bv_left   = f"{best_s * cell_pct:.1f}%"
    bv_width  = f"{(best_e - best_s + 1) * cell_pct:.1f}%"
    bv_center = f"{(best_s + best_e + 1) / 2 * cell_pct:.1f}%"

    cells_html = ""
    day_labels_html = ""
    for i, day in enumerate(cal_days):
        t = i / max(1, n_days - 1)
        col = _interp_bloom_color(t)
        is_peak = peak_start <= day <= peak_end
        try:
            day_label = day.strftime("%-d")
        except ValueError:
            day_label = day.strftime("%d").lstrip("0") or "0"
        day_color = "#ff8fa9" if is_peak else "#8b8597"
        cells_html += f'<div style="height:36px;border-radius:4px;background:{col};"></div>'
        day_labels_html += (
            f'<div style="text-align:center;font:600 10px/1 \'IBM Plex Mono\',monospace;color:{day_color};">'
            f'{day_label}</div>'
        )

    month_spans: list[tuple[str, int, int]] = []
    for i, day in enumerate(cal_days):
        month_name = day.strftime("%B")
        if not month_spans or month_spans[-1][0] != month_name:
            month_spans.append((month_name, i + 1, i + 1))
        else:
            month_spans[-1] = (month_name, month_spans[-1][1], i + 1)

    month_labels_html = "".join(
        f'<div style="grid-column:{s}/{e + 1};border-top:1px solid rgba(255,255,255,.13);'
        f'padding-top:6px;font:600 9px/1 \'IBM Plex Mono\',monospace;letter-spacing:2px;'
        f'color:#6f6a80;text-transform:uppercase;">{name}</div>'
        for name, s, e in month_spans
    )

    prose_html    = _prose_paragraph(first_bloom, peak_start, peak_end, hanafubuki_end, forecast_doy, hist_avg_doy)
    mae           = station_mae if station_mae is not None else global_mae
    accuracy_html = _accuracy_footnote(mae)

    return textwrap.dedent(f"""
    <div style="border-top:1px solid rgba(255,255,255,.1);padding-top:30px;margin-top:50px;position:relative;">

        <div style="margin-bottom:24px;">
            <div style="font:500 12px/1 'IBM Plex Mono',monospace;letter-spacing:2px;color:#e69bb4;margin-bottom:18px;">
                予報 &mdash; The forecast{estimated_html}
            </div>
            <h2 style="font:300 28px/1.15 'Newsreader',serif;color:#f6f1f4;margin:0 0 16px;">
                This spring in <em style="font-style:italic;color:#ff8fa9;">{station_display}</em>, day by day.
            </h2>
        </div>

        {prose_html}

        <div style="position:relative;margin-top:32px;">
            <div style="position:absolute;top:-24px;left:{bv_center};transform:translateX(-50%);
                display:flex;align-items:center;gap:6px;white-space:nowrap;z-index:4;">
                <span style="font:600 13px/1 'Shippori Mincho',serif;color:#ffffff;">見頃</span>
                <span style="font:600 9px/1 'IBM Plex Mono',monospace;letter-spacing:1.5px;color:#d8d2e0;text-transform:uppercase;">Best viewing</span>
            </div>

            <div style="position:relative;display:grid;grid-template-columns:repeat({n_days},1fr);gap:2px;">
                <div style="position:absolute;top:-2px;bottom:-2px;left:{bv_left};width:{bv_width};
                    border:2px solid rgba(255,255,255,1);border-radius:8px;
                    box-shadow:0 0 4px 1px rgba(255,255,255,.9),0 0 14px 4px rgba(255,255,255,.45),0 0 32px 8px rgba(255,255,255,.18),inset 0 0 14px 4px rgba(255,255,255,.35);
                    background:rgba(255,255,255,.06);
                    pointer-events:none;z-index:2;"></div>
                {cells_html}
            </div>

            <div style="display:grid;grid-template-columns:repeat({n_days},1fr);gap:2px;margin-top:8px;">
                {day_labels_html}
            </div>

            <div style="display:grid;grid-template-columns:repeat({n_days},1fr);gap:2px;margin-top:6px;">
                {month_labels_html}
            </div>
        </div>

        {accuracy_html}
    </div>
    """).strip()


def render_best_time_to_visit_card(
    station_name: str,
    forecast_df: pd.DataFrame,
) -> str:
    dates = get_best_visit_dates(forecast_df)

    if not dates["available"]:
        return textwrap.dedent(
            f"""
            <div class="best-visit-card">
                <h3>Best Time to Visit</h3>
                <p class="best-visit-subtitle">
                    No forecast available for this station.
                </p>
            </div>
            """
        ).strip()

    first_bloom = dates["first_bloom"]
    peak_start = dates["peak_start"]
    peak_end = dates["peak_end"]
    visit_start = dates["visit_start"]
    visit_end = dates["visit_end"]

    tick_1 = first_bloom
    tick_2 = visit_start + pd.Timedelta(days=2)
    tick_3 = peak_end + pd.Timedelta(days=1)
    tick_4 = visit_end + pd.Timedelta(days=2)

    first_bloom_label = format_inline_date(first_bloom)
    peak_range_label = format_range_compact(peak_start, peak_end)
    visit_range_label = format_range_compact(visit_start, visit_end)

    return textwrap.dedent(
        f"""
        <div class="best-visit-card">

            <h3>Best Time to Visit</h3>

            <div class="visit-timeline-labels">
                <div class="timeline-label label-first">
                    <span>
                        First<br>
                        bloom
                    </span>
                    <div class="dotted-line"></div>
                </div>

                <div class="timeline-label label-peak">
                    <span>
                        Peak<br>
                        bloom
                    </span>
                    <div class="dotted-line"></div>
                </div>

                <div class="timeline-label label-best">
                    <span>
                        Best time<br>
                        to visit
                    </span>
                    <div class="dotted-line"></div>
                </div>
            </div>

            <div class="visit-timeline-wrap">
                <div class="timeline-pale-track"></div>
                <div class="timeline-visit-window"></div>
                <div class="timeline-peak-window"></div>

                <div class="timeline-dot dot-first"></div>
                <div class="timeline-dot dot-peak"></div>
                <div class="timeline-dot dot-best"></div>
            </div>

            <div class="timeline-axis">
                <div class="axis-line"></div>

                <div class="axis-tick tick-one">
                    <div class="tick-mark"></div>
                    <div class="tick-date">{format_card_date(tick_1)}</div>
                </div>

                <div class="axis-tick tick-two">
                    <div class="tick-mark"></div>
                    <div class="tick-date">{format_card_date(tick_2)}</div>
                </div>

                <div class="axis-tick tick-three">
                    <div class="tick-mark"></div>
                    <div class="tick-date">{format_card_date(tick_3)}</div>
                </div>

                <div class="axis-tick tick-four">
                    <div class="tick-mark"></div>
                    <div class="tick-date">{format_card_date(tick_4)}</div>
                </div>
            </div>

            <div class="visit-detail-section">

                <div class="visit-detail-row">
                    <div class="visit-detail-dot"></div>
                    <div>
                        <div class="visit-detail-label">Estimated first bloom</div>
                        <div class="visit-detail-value">{first_bloom_label}</div>
                    </div>
                </div>

                <div class="visit-row-line"></div>

                <div class="visit-detail-row">
                    <div class="visit-detail-dot bright"></div>
                    <div>
                        <div class="visit-detail-label">Estimated peak bloom</div>
                        <div class="visit-detail-value">{peak_range_label}</div>
                    </div>
                </div>

                <div class="visit-row-line"></div>

                <div class="visit-detail-row">
                    <div class="visit-detail-dot medium"></div>
                    <div>
                        <div class="visit-detail-label">Best time to visit</div>
                        <div class="visit-detail-value">{visit_range_label}</div>
                    </div>
                </div>

            </div>

        </div>
        """
    ).strip()
