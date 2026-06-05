import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "./components/Layout";
import { Dashboard } from "./pages/Dashboard";
import { LinkBudgetPage } from "./pages/LinkBudgetPage";
import { RoutingPage } from "./pages/RoutingPage";
import { OrbitalPage } from "./pages/OrbitalPage";
import { SecurityPage } from "./pages/SecurityPage";
import { SimulationsPage } from "./pages/SimulationsPage";
import { CmdPage } from "./pages/CmdPage";
import "./styles/global.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="link-budget" element={<LinkBudgetPage />} />
          <Route path="routing" element={<RoutingPage />} />
          <Route path="orbital" element={<OrbitalPage />} />
          <Route path="security" element={<SecurityPage />} />
          <Route path="simulations" element={<SimulationsPage />} />
          <Route path="cmd" element={<CmdPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
