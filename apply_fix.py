import re, pathlib

def sub_file(path, old, new, must=True):
    p = pathlib.Path(path)
    text = p.read_text()
    if old not in text:
        if must:
            raise SystemExit(f"BLOCK NOT FOUND in {path}")
        return
    p.write_text(text.replace(old, new, 1))
    print(f"patched {path}")

# ---- discovery.py ----
sub_file("src/breakwater/discovery.py",
    "            n = int(np.isfinite(long_net).sum())\n"
    "            if n < MIN_SLICE_ROWS:\n"
    "                continue\n",
    "            n_long = int(np.isfinite(long_net).sum())\n"
    "            n_short = int(np.isfinite(short_net).sum())\n"
    "            if n_long < MIN_SLICE_ROWS or n_short < MIN_SLICE_ROWS:\n"
    "                continue\n")

discovery = pathlib.Path("src/breakwater/discovery.py").read_text()
old_side = """            if long_mean >= short_mean:
                side = "LONG"
                mean, median, hit_rate, t_stat, p_value = long_mean, long_median, long_hit, long_t, long_p
                ret_col = "fwd_trade_net_long"
            else:
                side = "SHORT"
                mean, median, hit_rate, t_stat, p_value = short_mean, short_median, short_hit, short_t, short_p
                ret_col = "fwd_trade_net_short"
"""
new_side = """            # Emit BOTH directions for every feature:state. Discovery must not
            # collapse a state to its single winning side, because that
            # structurally starves the SHORT pool: a state that is only mildly
            # long-biased over the full sample would otherwise never surface a
            # SHORT candidate even when the short side carries a real edge on
            # recent (bear) data. Validation re-evaluates each side on the
            # training window, so emitting both is safe and necessary.
            for side, n, mean, median, hit_rate, t_stat, p_value, ret_col in (
                ("LONG", n_long, long_mean, long_median, long_hit, long_t, long_p, "fwd_trade_net_long"),
                ("SHORT", n_short, short_mean, short_median, short_hit, short_t, short_p, "fwd_trade_net_short"),
            ):
"""
if old_side not in discovery:
    raise SystemExit("side block not found in discovery.py")
discovery = discovery.replace(old_side, new_side, 1)

# re-indent the append body inside the loop
old_append = """            asia_n, asia_mean, asia_hit = _session_stats_from_col(subset, mask, SESSION_ASIA, ret_col)
            eu_n, eu_mean, eu_hit = _session_stats_from_col(subset, mask, SESSION_EU, ret_col)
            us_n, us_mean, us_hit = _session_stats_from_col(subset, mask, SESSION_US, ret_col)

            candidates.append(
                SliceStat(
                    slice_id=f"{feature}:{state}:{side}",
                    kind=kind,
                    feature=feature,
                    state=state,
                    side=side,
                    n=n,
                    mean_ret_costadj=mean,
                    median_ret_costadj=median,
                    hit_rate=hit_rate,
                    t_stat=t_stat,
                    p_value=p_value,
                    bonferroni_pass=False,
                    horizon_bars=horizon_bars,
                    session_asia_n=asia_n,
                    session_asia_mean_ret_costadj=asia_mean,
                    session_asia_hit_rate=asia_hit,
                    session_eu_n=eu_n,
                    session_eu_mean_ret_costadj=eu_mean,
                    session_eu_hit_rate=eu_hit,
                    session_us_n=us_n,
                    session_us_mean_ret_costadj=us_mean,
                    session_us_hit_rate=us_hit,
                )
            )
            effective_tests += 2
"""
new_append = """                asia_n, asia_mean, asia_hit = _session_stats_from_col(
                    subset, mask, SESSION_ASIA, ret_col
                )
                eu_n, eu_mean, eu_hit = _session_stats_from_col(
                    subset, mask, SESSION_EU, ret_col
                )
                us_n, us_mean, us_hit = _session_stats_from_col(
                    subset, mask, SESSION_US, ret_col
                )

                candidates.append(
                    SliceStat(
                        slice_id=f"{feature}:{state}:{side}",
                        kind=kind,
                        feature=feature,
                        state=state,
                        side=side,
                        n=n,
                        mean_ret_costadj=mean,
                        median_ret_costadj=median,
                        hit_rate=hit_rate,
                        t_stat=t_stat,
                        p_value=p_value,
                        bonferroni_pass=False,
                        horizon_bars=horizon_bars,
                        session_asia_n=asia_n,
                        session_asia_mean_ret_costadj=asia_mean,
                        session_asia_hit_rate=asia_hit,
                        session_eu_n=eu_n,
                        session_eu_mean_ret_costadj=eu_mean,
                        session_eu_hit_rate=eu_hit,
                        session_us_n=us_n,
                        session_us_mean_ret_costadj=us_mean,
                        session_us_hit_rate=us_hit,
                    )
                )
            effective_tests += 2
"""
if old_append not in discovery:
    raise SystemExit("append block not found in discovery.py")
discovery = discovery.replace(old_append, new_append, 1)
pathlib.Path("src/breakwater/discovery.py").write_text(discovery)
print("patched src/breakwater/discovery.py (loop + indent)")

# ---- engine.py ----
sub_file("src/breakwater/engine.py",
    "    best = max(eligible, key=lambda row: row.mean_ret_costadj, default=None)\n"
    "    best_failing = max(\n"
    "        [row for row in eligible if not row.validated],\n"
    "        key=lambda row: row.mean_ret_costadj,\n"
    "        default=None,\n"
    "    )\n"
    "\n"
    "    reasons = Counter()\n"
    "    for row in eligible:\n",
    "    best = max(shorts_validated, key=lambda row: row.mean_ret_costadj, default=None)\n"
    "    best_failing = max(\n"
    "        [row for row in shorts_validated if not row.validated],\n"
    "        key=lambda row: row.mean_ret_costadj,\n"
    "        default=None,\n"
    "    )\n"
    "\n"
    "    reasons = Counter()\n"
    "    for row in shorts_validated:\n")

sub_file("src/breakwater/engine.py",
    '        "best_short_fail_reasons": str(best.fail_reasons or "") if best else "",\n'
    '        "best_failing_short_edge_bps":',
    '        "best_short_fail_reasons": str(best.fail_reasons or "") if best else "",\n'
    '        "best_short_n": int(getattr(best, "n", 0)) if best else 0,\n'
    '        "best_short_breadth": int(getattr(best, "breadth_symbols_used", 0)) if best else 0,\n'
    '        "best_short_regime_confounded": bool(getattr(best, "regime_confounded", False)) if best else False,\n'
    '        "best_failing_short_edge_bps":')

# ---- validation.py (comment only) ----
sub_file("src/breakwater/validation.py",
    '        side_train = "LONG" if mean_long_train >= mean_short_train else "SHORT"\n'
    "        direction_ok = (str(candidate.side).upper() == side_train)\n",
    '        side_train = "LONG" if mean_long_train >= mean_short_train else "SHORT"\n'
    "        # Reject a candidate whose side disagrees with the training-window\n"
    "        # preference rather than silently converting it here. This is safe\n"
    "        # because discovery now emits BOTH LONG and SHORT candidates for every\n"
    "        # feature:state, so the training-preferred side is validated as its own\n"
    "        # candidate. Converting here would double-emit the same slice_id and\n"
    "        # reintroduce the very side-selection leakage this gate guards against.\n"
    "        direction_ok = (str(candidate.side).upper() == side_train)\n")

print("ALL DONE")
