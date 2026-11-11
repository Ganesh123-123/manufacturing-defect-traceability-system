/**
 * Dashboard & Analytics Module
 * Industrial Manufacturing Quality Dashboard
 */
class DashboardModule {
    static chartInstances = {};

    static async init() {
        const container = document.getElementById("page-content");
        if (!container) return;

        container.innerHTML = `
            <!-- Live KPI Metrics Row -->
            <div class="row g-3 mb-4" id="kpi-row">
                <div class="col-12 text-center py-4">
                    <div class="spinner-border text-primary" role="status"></div>
                    <div class="mt-2 text-muted small">Loading Live Manufacturing Quality Metrics...</div>
                </div>
            </div>

            <!-- Charts Row 1: Monthly Trends (Line) & Rework vs Scrap (Doughnut) -->
            <div class="row g-3 mb-4">
                <div class="col-lg-8">
                    <div class="card-enterprise h-100">
                        <div class="card-header">
                            <h6 class="card-title">
                                <i class="fa-solid fa-chart-line text-primary me-2"></i>Monthly Defect, Scrap & Rework Trends
                            </h6>
                            <span class="badge badge-soft-primary">Live Database Audit</span>
                        </div>
                        <div class="card-body">
                            <div class="chart-container" id="monthlyTrendContainer" style="position: relative; height: 320px; width: 100%;">
                                <canvas id="monthlyTrendChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card-enterprise h-100">
                        <div class="card-header">
                            <h6 class="card-title">
                                <i class="fa-solid fa-chart-pie text-warning me-2"></i>Rework vs Scrap Volume
                            </h6>
                            <span class="badge badge-soft-warning">Disposition</span>
                        </div>
                        <div class="card-body d-flex flex-column align-items-center justify-content-center">
                            <div class="chart-container" id="reworkScrapContainer" style="position: relative; height: 230px; width: 100%; max-width: 280px;">
                                <canvas id="reworkScrapChart"></canvas>
                            </div>
                            <div class="mt-3 text-center w-100" id="rework-scrap-legend"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Charts Row 2: Supplier Defect Analysis & Machine Defect Analysis -->
            <div class="row g-3 mb-4">
                <div class="col-lg-6">
                    <div class="card-enterprise h-100">
                        <div class="card-header">
                            <h6 class="card-title">
                                <i class="fa-solid fa-truck-field text-info me-2"></i>Top Defective Suppliers
                            </h6>
                            <span class="badge badge-soft-info">Vendor Pareto</span>
                        </div>
                        <div class="card-body">
                            <div class="chart-container" id="supplierDefectContainer" style="position: relative; height: 280px; width: 100%;">
                                <canvas id="supplierDefectChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6">
                    <div class="card-enterprise h-100">
                        <div class="card-header">
                            <h6 class="card-title">
                                <i class="fa-solid fa-gears text-purple me-2"></i>Machine Defect & Scrap Analysis
                            </h6>
                            <span class="badge badge-soft-dark">Work Centers</span>
                        </div>
                        <div class="card-body">
                            <div class="chart-container" id="machineDefectContainer" style="position: relative; height: 280px; width: 100%;">
                                <canvas id="machineDefectChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Charts Row 3: Product Defect Rates, Inspection Pass/Fail, & CAPA Status -->
            <div class="row g-3 mb-4">
                <div class="col-lg-6">
                    <div class="card-enterprise h-100">
                        <div class="card-header">
                            <h6 class="card-title">
                                <i class="fa-solid fa-microchip text-danger me-2"></i>Highest Defect Rate Products (%)
                            </h6>
                            <span class="badge badge-soft-danger">Product Pareto</span>
                        </div>
                        <div class="card-body">
                            <div class="chart-container" id="productRateContainer" style="position: relative; height: 280px; width: 100%;">
                                <canvas id="productRateChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3">
                    <div class="card-enterprise h-100">
                        <div class="card-header">
                            <h6 class="card-title">
                                <i class="fa-solid fa-check-double text-success me-2"></i>Inspection Pass/Fail
                            </h6>
                        </div>
                        <div class="card-body d-flex flex-column align-items-center justify-content-center">
                            <div class="chart-container" id="passFailContainer" style="position: relative; height: 210px; width: 100%; max-width: 220px;">
                                <canvas id="passFailChart"></canvas>
                            </div>
                            <div class="mt-3 text-center w-100" id="pass-fail-legend"></div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-3">
                    <div class="card-enterprise h-100">
                        <div class="card-header">
                            <h6 class="card-title">
                                <i class="fa-solid fa-clipboard-check text-primary me-2"></i>CAPA Status
                            </h6>
                        </div>
                        <div class="card-body d-flex flex-column align-items-center justify-content-center">
                            <div class="chart-container" id="capaStatusContainer" style="position: relative; height: 210px; width: 100%; max-width: 220px;">
                                <canvas id="capaStatusChart"></canvas>
                            </div>
                            <div class="mt-3 text-center w-100" id="capa-status-legend"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        if (window.Chart) {
            Chart.defaults.color = "#94a3b8";
            Chart.defaults.borderColor = "rgba(71, 85, 105, 0.22)";
            if (Chart.defaults.plugins?.legend?.labels) {
                Chart.defaults.plugins.legend.labels.color = "#cbd5e1";
            }
            if (Chart.defaults.plugins?.tooltip) {
                Chart.defaults.plugins.tooltip.backgroundColor = "rgba(10, 15, 29, 0.95)";
                Chart.defaults.plugins.tooltip.borderColor = "rgba(56, 189, 248, 0.4)";
                Chart.defaults.plugins.tooltip.borderWidth = 1;
                Chart.defaults.plugins.tooltip.titleColor = "#ffffff";
                Chart.defaults.plugins.tooltip.bodyColor = "#cbd5e1";
            }
        }

        await this.loadKPIs();
        await this.loadAllCharts();
    }

    /**
     * Helper to safely destroy and re-create a chart instance on a canvas.
     */
    static safeGetContext(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return null;

        // Destroy Chart.js instance attached to this canvas if it exists
        const existing = Chart.getChart(canvas);
        if (existing) {
            existing.destroy();
        }
        if (this.chartInstances[canvasId]) {
            this.chartInstances[canvasId].destroy();
            delete this.chartInstances[canvasId];
        }

        return canvas.getContext("2d");
    }

    /**
     * Show clean empty-state fallback in container.
     */
    static showEmptyState(containerId, message = "No quality data available for this chart.") {
        const container = document.getElementById(containerId);
        if (!container) return;
        container.innerHTML = `
            <div class="d-flex flex-column align-items-center justify-content-center h-100 text-muted p-4">
                <i class="fa-solid fa-chart-simple fa-2x mb-2 text-secondary opacity-50"></i>
                <div class="small fw-semibold text-center">${message}</div>
            </div>
        `;
    }

    /**
     * Load Top KPI Cards from real MySQL API
     */
    static async loadKPIs() {
        try {
            const kpis = await ApiClient.get("/analytics/dashboard");
            const kpiRow = document.getElementById("kpi-row");
            if (!kpiRow) return;

            kpiRow.innerHTML = `
                <div class="col-xl-2 col-md-4 col-sm-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Total Products</h6>
                            <p class="kpi-value">${Number(kpis.total_products || 0).toLocaleString()}</p>
                            <span class="kpi-sub">Active SKUs</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-blue"><i class="fa-solid fa-boxes-stacked"></i></div>
                    </div>
                </div>
                <div class="col-xl-2 col-md-4 col-sm-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Suppliers</h6>
                            <p class="kpi-value">${Number(kpis.total_suppliers || 0).toLocaleString()}</p>
                            <span class="kpi-sub">Approved Vendors</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-cyan"><i class="fa-solid fa-truck"></i></div>
                    </div>
                </div>
                <div class="col-xl-2 col-md-4 col-sm-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Material Lots</h6>
                            <p class="kpi-value">${Number(kpis.total_material_lots || 0).toLocaleString()}</p>
                            <span class="kpi-sub">Pedigree Batches</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-purple"><i class="fa-solid fa-layer-group"></i></div>
                    </div>
                </div>
                <div class="col-xl-2 col-md-4 col-sm-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Work Orders</h6>
                            <p class="kpi-value">${Number(kpis.total_production_orders || 0).toLocaleString()}</p>
                            <span class="kpi-sub">Shop Floor Batches</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-blue"><i class="fa-solid fa-industry"></i></div>
                    </div>
                </div>
                <div class="col-xl-2 col-md-4 col-sm-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Inspections</h6>
                            <p class="kpi-value">${Number(kpis.total_inspections || 0).toLocaleString()}</p>
                            <span class="kpi-sub">${Number(kpis.total_inspected_units || 0).toLocaleString()} units</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-green"><i class="fa-solid fa-clipboard-check"></i></div>
                    </div>
                </div>
                <div class="col-xl-2 col-md-4 col-sm-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Total Defects</h6>
                            <p class="kpi-value text-danger">${Number(kpis.total_defects || 0).toLocaleString()}</p>
                            <span class="kpi-sub">${Number(kpis.total_defective_units || 0).toLocaleString()} units</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-red"><i class="fa-solid fa-triangle-exclamation"></i></div>
                    </div>
                </div>
                <div class="col-xl-3 col-md-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Defect Rate</h6>
                            <p class="kpi-value ${kpis.defect_rate > 5 ? 'text-danger' : 'text-primary'}">${kpis.defect_rate}%</p>
                            <span class="kpi-sub">Defective / Inspected Units</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-amber"><i class="fa-solid fa-percent"></i></div>
                    </div>
                </div>
                <div class="col-xl-3 col-md-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Rework Quantity</h6>
                            <p class="kpi-value text-warning">${Number(kpis.rework_quantity || 0).toLocaleString()}</p>
                            <span class="kpi-sub">Salvageable units</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-amber"><i class="fa-solid fa-wrench"></i></div>
                    </div>
                </div>
                <div class="col-xl-3 col-md-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Scrap Quantity</h6>
                            <p class="kpi-value text-danger">${Number(kpis.scrap_quantity || 0).toLocaleString()}</p>
                            <span class="kpi-sub">Disposed scrap units</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-red"><i class="fa-solid fa-trash-can"></i></div>
                    </div>
                </div>
                <div class="col-xl-3 col-md-6">
                    <div class="kpi-card">
                        <div class="kpi-info">
                            <h6>Open CAPAs</h6>
                            <p class="kpi-value text-purple">${Number(kpis.open_corrective_actions || 0).toLocaleString()}</p>
                            <span class="kpi-sub">Active investigations</span>
                        </div>
                        <div class="kpi-icon-wrap kpi-purple"><i class="fa-solid fa-shield-halved"></i></div>
                    </div>
                </div>
            `;
        } catch (e) {
            console.error("KPI Load Error:", e);
            const kpiRow = document.getElementById("kpi-row");
            if (kpiRow) {
                kpiRow.innerHTML = `
                    <div class="col-12"><div class="alert alert-danger"><i class="fa-solid fa-circle-exclamation me-2"></i>Failed to fetch live KPIs: ${e.message}</div></div>
                `;
            }
        }
    }

    /**
     * Concurrently initialize all 7 charts in parallel with error isolation.
     */
    static async loadAllCharts() {
        await Promise.allSettled([
            this.renderMonthlyTrendChart(),
            this.renderReworkScrapChart(),
            this.renderSupplierDefectChart(),
            this.renderMachineDefectChart(),
            this.renderProductRateChart(),
            this.renderPassFailChart(),
            this.renderCapaStatusChart()
        ]);
    }

    // -----------------------------------------------------------------
    // 1. Monthly Defect, Scrap & Rework Trends
    // -----------------------------------------------------------------
    static async renderMonthlyTrendChart() {
        try {
            const data = await ApiClient.get("/analytics/monthly-trends");
            const ctx = this.safeGetContext("monthlyTrendChart");
            if (!ctx) return;

            if (!data || data.length === 0) {
                this.showEmptyState("monthlyTrendContainer", "No monthly trend records logged yet.");
                return;
            }

            this.chartInstances["monthlyTrendChart"] = new Chart(ctx, {
                type: "line",
                data: {
                    labels: data.map(d => d.month || "2026"),
                    datasets: [
                        {
                            label: "Total Defects",
                            data: data.map(d => d.defect_count || 0),
                            borderColor: "#ef4444",
                            backgroundColor: "rgba(239, 68, 68, 0.12)",
                            fill: true,
                            tension: 0.35,
                            borderWidth: 2.5,
                            pointRadius: 4,
                            pointHoverRadius: 6
                        },
                        {
                            label: "Rework Units",
                            data: data.map(d => d.rework_quantity || 0),
                            borderColor: "#f59e0b",
                            backgroundColor: "rgba(245, 158, 11, 0.05)",
                            tension: 0.35,
                            borderWidth: 2,
                            pointRadius: 3
                        },
                        {
                            label: "Scrap Units",
                            data: data.map(d => d.scrap_quantity || 0),
                            borderColor: "#b91c1c",
                            borderDash: [5, 5],
                            tension: 0.35,
                            borderWidth: 2,
                            pointRadius: 3
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: "top", labels: { boxWidth: 14, font: { size: 12 } } },
                        tooltip: { mode: "index", intersect: false }
                    },
                    scales: {
                        y: { beginAtZero: true, grid: { color: "rgba(71, 85, 105, 0.2)" } },
                        x: { grid: { display: false } }
                    }
                }
            });
        } catch (e) {
            console.error("Monthly Trends Error:", e);
            this.showEmptyState("monthlyTrendContainer", `Failed to load monthly trends: ${e.message}`);
        }
    }

    // -----------------------------------------------------------------
    // 2. Rework vs Scrap Volume
    // -----------------------------------------------------------------
    static async renderReworkScrapChart() {
        try {
            const data = await ApiClient.get("/analytics/rework-vs-scrap");
            const ctx = this.safeGetContext("reworkScrapChart");
            if (!ctx) return;

            const rework = Number(data.rework || 0);
            const scrap = Number(data.scrap || 0);
            const total = rework + scrap;

            if (total === 0) {
                this.showEmptyState("reworkScrapContainer", "Zero rework or scrap records logged.");
                return;
            }

            this.chartInstances["reworkScrapChart"] = new Chart(ctx, {
                type: "doughnut",
                data: {
                    labels: ["Rework Units", "Scrap Units"],
                    datasets: [{
                        data: [rework, scrap],
                        backgroundColor: ["#f59e0b", "#ef4444"],
                        hoverBackgroundColor: ["#d97706", "#dc2626"],
                        borderWidth: 2,
                        borderColor: "rgba(10, 15, 29, 0.95)"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: "65%",
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const val = context.raw || 0;
                                    const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                                    return ` ${context.label}: ${val.toLocaleString()} (${pct}%)`;
                                }
                            }
                        }
                    }
                }
            });

            const legendEl = document.getElementById("rework-scrap-legend");
            if (legendEl) {
                legendEl.innerHTML = `
                    <div class="d-flex justify-content-center gap-2 flex-wrap">
                        <span class="badge badge-soft-warning py-1 px-2">
                            <i class="fa-solid fa-wrench me-1"></i>Rework: ${rework.toLocaleString()} (${data.rework_percentage}%)
                        </span>
                        <span class="badge badge-soft-danger py-1 px-2">
                            <i class="fa-solid fa-trash-can me-1"></i>Scrap: ${scrap.toLocaleString()} (${data.scrap_percentage}%)
                        </span>
                    </div>
                `;
            }
        } catch (e) {
            console.error("Rework vs Scrap Error:", e);
            this.showEmptyState("reworkScrapContainer", `Failed to load rework/scrap: ${e.message}`);
        }
    }

    // -----------------------------------------------------------------
    // 3. Top Defective Suppliers (Pareto Bar Chart)
    // -----------------------------------------------------------------
    static async renderSupplierDefectChart() {
        try {
            const suppliers = await ApiClient.get("/analytics/suppliers");
            const ctx = this.safeGetContext("supplierDefectChart");
            if (!ctx) return;

            if (!suppliers || suppliers.length === 0) {
                this.showEmptyState("supplierDefectContainer", "No supplier defect records found.");
                return;
            }

            const labels = suppliers.map(s => {
                const name = s.supplier_name || "Unknown Supplier";
                return name.length > 18 ? name.substring(0, 16) + "..." : name;
            });
            const counts = suppliers.map(s => s.defect_count || 0);
            const units = suppliers.map(s => s.defective_units || 0);

            this.chartInstances["supplierDefectChart"] = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "Defect Incidents",
                            data: counts,
                            backgroundColor: "#0ea5e9",
                            hoverBackgroundColor: "#0284c7",
                            borderRadius: 4
                        },
                        {
                            label: "Defective Units",
                            data: units,
                            backgroundColor: "#38bdf8",
                            hoverBackgroundColor: "#0ea5e9",
                            borderRadius: 4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: "top", labels: { boxWidth: 12 } },
                        tooltip: {
                            callbacks: {
                                title: function(context) {
                                    const idx = context[0].dataIndex;
                                    return suppliers[idx].supplier_name;
                                }
                            }
                        }
                    },
                    scales: {
                        y: { beginAtZero: true, grid: { color: "rgba(71, 85, 105, 0.2)" } },
                        x: { grid: { display: false }, ticks: { maxRotation: 30, font: { size: 10 } } }
                    }
                }
            });
        } catch (e) {
            console.error("Supplier Defect Chart Error:", e);
            this.showEmptyState("supplierDefectContainer", `Failed to load supplier defects: ${e.message}`);
        }
    }

    // -----------------------------------------------------------------
    // 4. Machine Defect & Scrap Analysis (Stacked Bar Chart)
    // -----------------------------------------------------------------
    static async renderMachineDefectChart() {
        try {
            const machines = await ApiClient.get("/analytics/machines");
            const ctx = this.safeGetContext("machineDefectChart");
            if (!ctx) return;

            if (!machines || machines.length === 0) {
                this.showEmptyState("machineDefectContainer", "No machine non-conformance records found.");
                return;
            }

            const labels = machines.map(m => m.machine_name || "Machine");
            const reworkData = machines.map(m => m.rework_quantity || 0);
            const scrapData = machines.map(m => m.scrap_quantity || 0);

            this.chartInstances["machineDefectChart"] = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "Rework Units",
                            data: reworkData,
                            backgroundColor: "#f59e0b",
                            hoverBackgroundColor: "#d97706",
                            borderRadius: 4
                        },
                        {
                            label: "Scrap Units",
                            data: scrapData,
                            backgroundColor: "#ef4444",
                            hoverBackgroundColor: "#dc2626",
                            borderRadius: 4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: "top", labels: { boxWidth: 12 } },
                        tooltip: { mode: "index", intersect: false }
                    },
                    scales: {
                        x: { stacked: true, grid: { display: false }, ticks: { maxRotation: 35, font: { size: 10 } } },
                        y: { stacked: true, beginAtZero: true, grid: { color: "rgba(71, 85, 105, 0.2)" } }
                    }
                }
            });
        } catch (e) {
            console.error("Machine Defect Chart Error:", e);
            this.showEmptyState("machineDefectContainer", `Failed to load machine defects: ${e.message}`);
        }
    }

    // -----------------------------------------------------------------
    // 5. Highest Defect Rate Products (%)
    // -----------------------------------------------------------------
    static async renderProductRateChart() {
        try {
            const products = await ApiClient.get("/analytics/products");
            const ctx = this.safeGetContext("productRateChart");
            if (!ctx) return;

            if (!products || products.length === 0) {
                this.showEmptyState("productRateContainer", "No product inspection data available.");
                return;
            }

            const labels = products.map(p => p.product_sku);
            const rates = products.map(p => p.defect_rate || 0);

            this.chartInstances["productRateChart"] = new Chart(ctx, {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [{
                        label: "Defect Rate (%)",
                        data: rates,
                        backgroundColor: "#8b5cf6",
                        hoverBackgroundColor: "#7c3aed",
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                title: function(context) {
                                    const idx = context[0].dataIndex;
                                    return `${products[idx].product_sku} - ${products[idx].product_name}`;
                                },
                                label: function(context) {
                                    const idx = context.dataIndex;
                                    const p = products[idx];
                                    return ` Defect Rate: ${p.defect_rate}% (Failed: ${p.failed_quantity} / Inspected: ${p.inspected_quantity.toLocaleString()})`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { callback: v => v + "%" },
                            grid: { color: "rgba(71, 85, 105, 0.2)" }
                        },
                        x: { grid: { display: false }, ticks: { font: { size: 10 } } }
                    }
                }
            });
        } catch (e) {
            console.error("Product Rate Chart Error:", e);
            this.showEmptyState("productRateContainer", `Failed to load product defect rates: ${e.message}`);
        }
    }

    // -----------------------------------------------------------------
    // 6. Inspection Pass vs Fail
    // -----------------------------------------------------------------
    static async renderPassFailChart() {
        try {
            const data = await ApiClient.get("/analytics/pass-fail");
            const ctx = this.safeGetContext("passFailChart");
            if (!ctx) return;

            const passed = Number(data.passed_quantity || 0);
            const failed = Number(data.failed_quantity || 0);
            const total = passed + failed;

            if (total === 0) {
                this.showEmptyState("passFailContainer", "No inspection results recorded.");
                return;
            }

            this.chartInstances["passFailChart"] = new Chart(ctx, {
                type: "pie",
                data: {
                    labels: ["Passed Units", "Failed Units"],
                    datasets: [{
                        data: [passed, failed],
                        backgroundColor: ["#10b981", "#ef4444"],
                        hoverBackgroundColor: ["#059669", "#dc2626"],
                        borderWidth: 2,
                        borderColor: "rgba(10, 15, 29, 0.95)"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const val = context.raw || 0;
                                    const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                                    return ` ${context.label}: ${val.toLocaleString()} (${pct}%)`;
                                }
                            }
                        }
                    }
                }
            });

            const legendEl = document.getElementById("pass-fail-legend");
            if (legendEl) {
                legendEl.innerHTML = `
                    <div class="d-flex justify-content-center gap-2 flex-wrap">
                        <span class="badge badge-soft-success py-1 px-2">
                            <i class="fa-solid fa-circle-check me-1"></i>Pass: ${data.pass_rate}%
                        </span>
                        <span class="badge badge-soft-danger py-1 px-2">
                            <i class="fa-solid fa-circle-xmark me-1"></i>Fail: ${data.fail_rate}%
                        </span>
                    </div>
                `;
            }
        } catch (e) {
            console.error("Pass/Fail Chart Error:", e);
            this.showEmptyState("passFailContainer", `Failed to load pass/fail: ${e.message}`);
        }
    }

    // -----------------------------------------------------------------
    // 7. CAPA Status Distribution
    // -----------------------------------------------------------------
    static async renderCapaStatusChart() {
        try {
            const data = await ApiClient.get("/analytics/capa-distribution");
            const ctx = this.safeGetContext("capaStatusChart");
            if (!ctx) return;

            const labels = Object.keys(data);
            const values = Object.values(data).map(Number);
            const total = values.reduce((a, b) => a + b, 0);

            if (total === 0) {
                this.showEmptyState("capaStatusContainer", "No CAPA investigations logged.");
                return;
            }

            this.chartInstances["capaStatusChart"] = new Chart(ctx, {
                type: "doughnut",
                data: {
                    labels: labels,
                    datasets: [{
                        data: values,
                        backgroundColor: [
                            "#3b82f6", // OPEN
                            "#f59e0b", // IN_PROGRESS
                            "#ec4899", // CONTAINMENT
                            "#8b5cf6", // PENDING_VERIFICATION
                            "#10b981", // VERIFIED
                            "#64748b"  // CLOSED
                        ],
                        borderWidth: 2,
                        borderColor: "rgba(10, 15, 29, 0.95)"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: "60%",
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const val = context.raw || 0;
                                    const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                                    return ` ${context.label}: ${val.toLocaleString()} (${pct}%)`;
                                }
                            }
                        }
                    }
                }
            });

            const legendEl = document.getElementById("capa-status-legend");
            if (legendEl) {
                legendEl.innerHTML = `
                    <div class="d-flex justify-content-center gap-1 flex-wrap small">
                        <span class="badge badge-soft-warning">In Prog: ${data.IN_PROGRESS || 0}</span>
                        <span class="badge badge-soft-info">Verified: ${data.VERIFIED || 0}</span>
                        <span class="badge badge-soft-success">Closed: ${data.CLOSED || 0}</span>
                    </div>
                `;
            }
        } catch (e) {
            console.error("CAPA Status Chart Error:", e);
            this.showEmptyState("capaStatusContainer", `Failed to load CAPA status: ${e.message}`);
        }
    }
}
