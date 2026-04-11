(() => {
  const hiddenBadge =
    "inline-flex items-center rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-bold uppercase tracking-[0.16em] text-slate-600";
  const pendingBadge =
    "inline-flex items-center rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-bold uppercase tracking-[0.16em] text-amber-700";
  const successBadge =
    "inline-flex items-center rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-bold uppercase tracking-[0.16em] text-emerald-700";

  function connect(url, handlers, retryMs = 3000) {
    let socket;
    const retry = () => setTimeout(() => connect(url, handlers, retryMs), retryMs);
    try {
      socket = new WebSocket(url.replace(/^http/, "ws"));
    } catch (e) {
      retry();
      return;
    }
    socket.onopen = () => handlers.onOpen && handlers.onOpen();
    socket.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (handlers[data.event]) handlers[data.event](data);
      } catch (_) {}
    };
    socket.onclose = () => retry();
    socket.onerror = () => {
      try {
        socket.close();
      } catch (_) {}
    };
    return socket;
  }

  function updateDealBlock(root, payload) {
    if (!root || !payload) return;
    const set = (id, text) => {
      const el = root.querySelector(`#${id}`);
      if (el) el.textContent = text;
    };
    set("deal-overall", payload.status_display || payload.status || "Unknown");
    set("deal-progress", payload.progress || "");
    const decisionLabel = (state) =>
      state === "accepted" ? "Accepted" : state === "rejected" ? "Rejected" : "Pending";
    set(
      "deal-buyer",
      decisionLabel(
        payload.buyer_decision ||
          (payload.buyer_rejected ? "rejected" : payload.buyer_accepted ? "accepted" : "pending")
      )
    );
    set(
      "deal-seller",
      decisionLabel(
        payload.seller_decision ||
          (payload.seller_rejected ? "rejected" : payload.seller_accepted ? "accepted" : "pending")
      )
    );
    set(
      "deal-admin",
      payload.admin_decision
        ? payload.admin_decision === "approved"
          ? "Approved"
          : payload.admin_decision === "rejected"
          ? "Rejected"
          : "Pending"
        : "Pending"
    );
    set("deal-next", payload.next_action || "");
    set("deal-latest", payload.latest_event || "");
    const toggle = (selector, allowed) => {
      root.querySelectorAll(selector).forEach((btn) => {
        btn.style.display = allowed ? "inline-block" : "none";
        btn.disabled = !allowed;
      });
    };
    toggle(".deal-accept-form button", payload.can_accept);
    toggle(".deal-reject-form button", payload.can_reject);
    toggle(".deal-cancel-form button", payload.can_cancel);
    // Identity badges + labels
    const statusBadge = (id, state) => {
      const el = root.querySelector(`#${id}`);
      if (!el) return;
      el.className =
        state === "revealed" ? successBadge : state === "pending" ? pendingBadge : hiddenBadge;
      el.textContent =
        state === "revealed" ? "Identity revealed" : state === "pending" ? "Reveal pending" : "Identity hidden";
    };
    if (payload.buyer_identity_status) statusBadge("identity-buyer-status", payload.buyer_identity_status);
    if (payload.seller_identity_status) statusBadge("identity-seller-status", payload.seller_identity_status);
    if (payload.buyer_label) set("identity-buyer-label", payload.buyer_label);
    if (payload.seller_label) set("identity-seller-label", payload.seller_label);
    // Identity action buttons (viewer-specific booleans)
    const showBtn = (selector, show) => {
      root.querySelectorAll(selector).forEach((btn) => {
        btn.style.display = show ? "inline-block" : "none";
      });
    };
    if ("can_reveal_buyer" in payload) showBtn(".btn-reveal-buyer", payload.can_reveal_buyer);
    if ("can_reveal_seller" in payload) showBtn(".btn-reveal-seller", payload.can_reveal_seller);
    if ("can_request_buyer" in payload) showBtn(".btn-request-buyer", payload.can_request_buyer);
    if ("can_request_seller" in payload) showBtn(".btn-request-seller", payload.can_request_seller);
    const hist = root.querySelector("#deal-history-list");
    if (hist && payload.history) {
      hist.innerHTML = "";
      payload.history.forEach((h) => {
        const li = document.createElement("li");
        li.textContent = `${h.text} (${h.ts})`;
        hist.appendChild(li);
      });
    }
  }

  function initDealLive() {
    document.querySelectorAll("#deal-live").forEach((root) => {
      const statusUrl = root.dataset.statusUrl;
      const dealId = root.dataset.dealId;
      const wsUrl = `${window.location.protocol}//${window.location.host}/ws/deal/${dealId}/`;
      const fetchStatus = () => {
        fetch(statusUrl)
          .then((r) => r.json())
          .then((data) => updateDealBlock(root, data))
          .catch(() => {});
      };
      connect(wsUrl, {
        deal_update: (data) => {
          updateDealBlock(root, data.payload);
          fetchStatus(); // get viewer-specific booleans/labels immediately
        },
        typing: () => {},
        onOpen: fetchStatus,
      });
      // fallback poll every 10s
      setInterval(fetchStatus, 10000);
      // init immediately
      fetchStatus();
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initDealLive();
  });
})();
