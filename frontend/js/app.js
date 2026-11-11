/**
 * Main Single Page Application Router & UI Controller
 */
class App {
    constructor() {
        this.currentPage = "dashboard";
        this.init();
    }

    async init() {
        this.setupTheme();
        this.setupNavigation();
        this.checkServerHealth();
        // Periodically poll server health
        setInterval(() => this.checkServerHealth(), 15000);

        // Check hash or default to dashboard
        const hash = window.location.hash.replace("#", "") || "dashboard";
        this.navigate(hash);
    }

    setupTheme() {
        const savedTheme = localStorage.getItem("mfg-theme") || "dark";
        document.documentElement.setAttribute("data-theme", savedTheme);
        document.documentElement.setAttribute("data-bs-theme", "dark");
        this.updateThemeButton(savedTheme);

        const themeToggle = document.getElementById("theme-toggle");
        themeToggle?.addEventListener("click", () => {
            const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
            const newTheme = currentTheme === "dark" ? "deep-dark" : "dark";
            document.documentElement.setAttribute("data-theme", newTheme);
            document.documentElement.setAttribute("data-bs-theme", "dark");
            localStorage.setItem("mfg-theme", newTheme);
            this.updateThemeButton(newTheme);
        });
    }

    updateThemeButton(theme) {
        const themeToggle = document.getElementById("theme-toggle");
        if (!themeToggle) return;
        if (theme === "deep-dark") {
            themeToggle.innerHTML = '<i class="fa-solid fa-bolt text-cyan me-1"></i> <span>Obsidian Dark</span>';
            themeToggle.classList.add("active");
        } else {
            themeToggle.innerHTML = '<i class="fa-solid fa-moon text-primary me-1"></i> <span>Cyber Dark</span>';
            themeToggle.classList.remove("active");
        }
    }

    setupNavigation() {
        const sidebarToggle = document.getElementById("sidebar-toggle");
        const sidebarBackdrop = document.getElementById("sidebar-backdrop");

        sidebarToggle?.addEventListener("click", () => {
            const isOpen = document.body.classList.toggle("sidebar-open");
            sidebarToggle.setAttribute("aria-expanded", String(isOpen));
            sidebarToggle.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
        });

        sidebarBackdrop?.addEventListener("click", () => this.closeSidebar());

        document.querySelectorAll(".sidebar-menu a[data-page]").forEach(link => {
            link.addEventListener("click", (e) => {
                e.preventDefault();
                const page = link.getAttribute("data-page");
                this.navigate(page);
                this.closeSidebar();
            });
        });

        window.addEventListener("hashchange", () => {
            const hash = window.location.hash.replace("#", "");
            if (hash && hash !== this.currentPage) {
                this.navigate(hash);
            }
        });
    }

    closeSidebar() {
        document.body.classList.remove("sidebar-open");
        const sidebarToggle = document.getElementById("sidebar-toggle");
        sidebarToggle?.setAttribute("aria-expanded", "false");
        sidebarToggle?.setAttribute("aria-label", "Open navigation");
    }

    navigate(pageName, traceQuery = null) {
        this.currentPage = pageName;
        window.location.hash = pageName;

        // Update active class on sidebar
        document.querySelectorAll(".sidebar-menu a[data-page]").forEach(link => {
            if (link.getAttribute("data-page") === pageName) {
                link.classList.add("active");
            } else {
                link.classList.remove("active");
            }
        });

        // Update top navbar title
        const titles = {
            dashboard: "Executive Manufacturing Quality Dashboard",
            products: "Finished Goods & Product Master Catalog",
            bom: "Bill of Materials (BOM) Architecture",
            suppliers: "Vendor Pedigree & Supplier Network",
            lots: "Material Lot Pedigree & Traceability",
            orders: "Shop Floor Production Orders & Consumptions",
            machines: "Machine Cells & Work Centers",
            steps: "Process Steps & Standard Operating Procedures",
            inspections: "Quality Inspection Checkpoints",
            defects: "Non-Conformance & Defect Management",
            capa: "Corrective & Preventive Action (CAPA) Lifecycle",
            traceability: "Multi-Tier Defect & Material Traceability",
            reports: "Quality Analytics, Exports & Verification Audit"
        };
        const pageTitleEl = document.getElementById("current-page-title");
        if (pageTitleEl) {
            pageTitleEl.innerText = titles[pageName] || "Manufacturing Quality System";
        }

        // Render target page
        switch (pageName) {
            case "dashboard":
                DashboardModule.init();
                break;
            case "products":
                Modules.renderProducts(1);
                break;
            case "bom":
                Modules.renderBOM();
                break;
            case "suppliers":
                Modules.renderSuppliers(1);
                break;
            case "lots":
                Modules.renderLots(1);
                break;
            case "orders":
                Modules.renderOrders(1);
                break;
            case "machines":
                Modules.renderMachines();
                break;
            case "steps":
                Modules.renderProcessSteps();
                break;
            case "inspections":
                Modules.renderInspections(1);
                break;
            case "defects":
                Modules.renderDefects(1);
                break;
            case "capa":
                Modules.renderCAPA(1);
                break;
            case "traceability":
                TraceabilityModule.init(
                    traceQuery ? traceQuery.type : undefined,
                    traceQuery ? traceQuery.id : undefined
                );
                break;
            case "reports":
                Modules.renderReports();
                break;
            default:
                DashboardModule.init();
        }
    }

    async checkServerHealth() {
        const badge = document.getElementById("server-status-pill");
        if (!badge) return;

        try {
            const health = await ApiClient.checkHealth();
            if (health.status === "healthy") {
                badge.className = "nav-status-badge";
                badge.innerHTML = `<span class="status-dot"></span> MySQL Connected (API 5000)`;
            } else {
                badge.className = "nav-status-badge text-warning bg-warning-subtle border-warning";
                badge.innerHTML = `<span class="status-dot bg-warning"></span> Degraded (${health.database})`;
            }
        } catch (e) {
            badge.className = "nav-status-badge text-danger bg-danger-subtle border-danger";
            badge.innerHTML = `<span class="status-dot bg-danger"></span> API Disconnected`;
        }
    }

    showToast(message, type = "info") {
        const toastContainer = document.getElementById("toast-container");
        if (!toastContainer) return;

        const id = "toast-" + Date.now();
        const icon = type === "success" ? "fa-circle-check text-success" :
                     type === "danger" ? "fa-circle-xmark text-danger" :
                     type === "warning" ? "fa-triangle-exclamation text-warning" : "fa-circle-info text-primary";

        const toastHtml = `
            <div id="${id}" class="toast toast-glass align-items-center border-0 shadow-lg mb-2" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body d-flex align-items-center gap-2">
                        <i class="fa-solid ${icon} fs-5"></i>
                        <span class="text-main">${message}</span>
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        toastContainer.insertAdjacentHTML("beforeend", toastHtml);
        const toastEl = document.getElementById(id);
        const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
        toast.show();
        toastEl.addEventListener("hidden.bs.toast", () => toastEl.remove());
    }
}

// Global app instance
let app;
document.addEventListener("DOMContentLoaded", () => {
    app = new App();
});
