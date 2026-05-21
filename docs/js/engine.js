const AetherixEngine = (() => {
  const SPEED_OF_LIGHT = 299792458;
  const SPEED_OF_LIGHT_KMS = 299792.458;
  const AU_KM = 149597870.7;
  const DEFAULT_WAVELENGTH = 1550e-9;
  const EARTH_PERIOD = 365.25;
  const MARS_PERIOD = 686.98;
  const SYNODIC_PERIOD = 779.94;

  const ORBITAL_ELEMENTS = {
    earth: {
      semiMajorAxisAU: 1.00000261,
      eccentricity: 0.01671123,
      inclinationDeg: 0.00005,
      raanDeg: -11.26064,
      argPeriapsisDeg: 102.94719,
      meanAnomalyDeg: 100.46435
    },
    mars: {
      semiMajorAxisAU: 1.52371034,
      eccentricity: 0.09339410,
      inclinationDeg: 1.84969142,
      raanDeg: 49.55953,
      argPeriapsisDeg: 286.53650,
      meanAnomalyDeg: 355.45332
    }
  };

  const LinkBudget = {
    freeSpaceLoss(distanceKm, wavelengthM) {
      wavelengthM = wavelengthM || DEFAULT_WAVELENGTH;
      const distM = distanceKm * 1000;
      const fspl = Math.pow((4 * Math.PI * distM) / wavelengthM, 2);
      return -10 * Math.log10(fspl);
    },

    antennaGain(apertureM, efficiency, wavelengthM) {
      wavelengthM = wavelengthM || DEFAULT_WAVELENGTH;
      efficiency = efficiency || 0.55;
      const gain = efficiency * Math.pow((Math.PI * apertureM) / wavelengthM, 2);
      return 10 * Math.log10(gain);
    },

    wattsToDbm(watts) {
      return 10 * Math.log10(watts * 1000);
    },

    oneWayLightTime(distanceKm) {
      return (distanceKm * 1000) / SPEED_OF_LIGHT;
    },

    calculate(params) {
      const wavelengthM = params.wavelengthM || DEFAULT_WAVELENGTH;
      const txPowerDbm = this.wattsToDbm(params.txPowerWatts || 5.0);
      const txGainDb = this.antennaGain(params.txApertureM || 0.22, params.txEfficiency || 0.55, wavelengthM);
      const eirpDbm = txPowerDbm + txGainDb + (params.txPointingLossDb || -1.0) + (params.txOpticsEffDb || -2.0);
      const fsplDb = this.freeSpaceLoss(params.distanceKm, wavelengthM);
      const rxGainDb = this.antennaGain(params.rxApertureM || 1.0, params.rxEfficiency || 0.55, wavelengthM);
      const rxPowerDbm = eirpDbm + fsplDb + (params.atmosphericLossDb || -3.0) + rxGainDb + (params.rxOpticsEffDb || -2.0) + (params.rxPointingLossDb || -0.5) + (params.implementationLossDb || -2.0);
      const rxSensitivityDbm = -50 + 10 * Math.log10(params.dataRateMbps || 10.0);
      const linkMarginDb = rxPowerDbm - rxSensitivityDbm - (params.requiredSnrDb || 10.0);
      const lightTime = this.oneWayLightTime(params.distanceKm);

      return {
        transmitterPowerDbm: txPowerDbm,
        transmitterAntennaGainDb: txGainDb,
        transmitterPointingLossDb: params.txPointingLossDb || -1.0,
        transmitterOpticsEffDb: params.txOpticsEffDb || -2.0,
        eirpDbm: eirpDbm,
        freeSpaceLossDb: fsplDb,
        atmosphericLossDb: params.atmosphericLossDb || -3.0,
        distanceKm: params.distanceKm,
        receiverAntennaGainDb: rxGainDb,
        receiverOpticsEffDb: params.rxOpticsEffDb || -2.0,
        receiverPointingLossDb: params.rxPointingLossDb || -0.5,
        implementationLossDb: params.implementationLossDb || -2.0,
        requiredSnrDb: params.requiredSnrDb || 10.0,
        receivedPowerDbm: rxPowerDbm,
        linkMarginDb: linkMarginDb,
        dataRateMbps: params.dataRateMbps || 10.0,
        lightTimeSeconds: lightTime,
        lightTimeMinutes: lightTime / 60,
        linkStatus: linkMarginDb > 0 ? 'POSITIVE' : 'NEGATIVE'
      };
    },

    marsScenarios() {
      const base = { txPowerWatts: 5.0, txApertureM: 0.22, rxApertureM: 1.0, dataRateMbps: 10.0 };
      return {
        minimum: this.calculate({ ...base, distanceKm: 55000000 }),
        average: this.calculate({ ...base, distanceKm: 225000000 }),
        maximum: this.calculate({ ...base, distanceKm: 390000000 })
      };
    }
  };

  const Orbital = {
    orbitalRadius(elements, trueAnomalyDeg) {
      const nu = trueAnomalyDeg * Math.PI / 180;
      const a = elements.semiMajorAxisAU;
      const e = elements.eccentricity;
      return a * (1 - e * e) / (1 + e * Math.cos(nu));
    },

    positionHeliocentric(elements, trueAnomalyDeg) {
      const r = this.orbitalRadius(elements, trueAnomalyDeg);
      const nu = trueAnomalyDeg * Math.PI / 180;
      const omega = elements.argPeriapsisDeg * Math.PI / 180;
      const Omega = elements.raanDeg * Math.PI / 180;
      const i = elements.inclinationDeg * Math.PI / 180;
      const xOrb = r * Math.cos(nu);
      const yOrb = r * Math.sin(nu);
      const x = xOrb * (Math.cos(omega) * Math.cos(Omega) - Math.sin(omega) * Math.sin(Omega) * Math.cos(i));
      const y = xOrb * (Math.cos(omega) * Math.sin(Omega) + Math.sin(omega) * Math.cos(Omega) * Math.cos(i));
      const z = xOrb * Math.sin(omega) * Math.sin(i) + yOrb * Math.cos(omega) * Math.sin(i);
      return { x, y, z };
    },

    earthMarsDistance(earthAnomalyDeg, marsAnomalyDeg) {
      const ePos = this.positionHeliocentric(ORBITAL_ELEMENTS.earth, earthAnomalyDeg);
      const mPos = this.positionHeliocentric(ORBITAL_ELEMENTS.mars, marsAnomalyDeg);
      const dx = mPos.x - ePos.x;
      const dy = mPos.y - ePos.y;
      const dz = mPos.z - ePos.z;
      return Math.sqrt(dx * dx + dy * dy + dz * dz) * AU_KM;
    },

    lightTime(distanceKm) {
      return distanceKm / SPEED_OF_LIGHT_KMS;
    },

    estimateDataRate(distanceKm) {
      const minDist = 54.6e6;
      const maxRate = 200.0;
      const rate = maxRate * Math.pow(minDist / distanceKm, 2);
      return Math.max(2.0, Math.min(200.0, rate));
    },

    dopplerShift(velocityKms, frequencyHz) {
      return frequencyHz * (velocityKms / SPEED_OF_LIGHT_KMS);
    },

    distanceTimeline(numPoints) {
      numPoints = numPoints || 780;
      const timeline = [];
      for (let day = 0; day < numPoints; day++) {
        const earthAnom = (day * 360 / EARTH_PERIOD) % 360;
        const marsAnom = (180 + day * 360 / MARS_PERIOD) % 360;
        const distKm = this.earthMarsDistance(earthAnom, marsAnom);
        const ltMin = this.lightTime(distKm) / 60;
        timeline.push({ day, distanceKm: distKm, distanceMKm: distKm / 1e6, lightTimeMin: ltMin, dataRateMbps: this.estimateDataRate(distKm) });
      }
      return timeline;
    },

    contactWindows(startDay, durationDays) {
      const windows = [];
      for (let day = startDay; day < startDay + durationDays; day++) {
        const earthAnom = (day * 360 / EARTH_PERIOD) % 360;
        const marsAnom = (180 + day * 360 / MARS_PERIOD) % 360;
        const distKm = this.earthMarsDistance(earthAnom, marsAnom);
        let phaseAngle = Math.abs(marsAnom - earthAnom);
        if (phaseAngle > 180) phaseAngle = 360 - phaseAngle;
        if (phaseAngle < 10) continue;
        const baseDuration = 8.0;
        const durationFactor = Math.sin(phaseAngle * Math.PI / 180);
        const duration = baseDuration * durationFactor;
        if (duration < 2) continue;
        windows.push({
          day,
          durationHours: duration,
          distanceKm: distKm,
          distanceMKm: distKm / 1e6,
          maxDataRateMbps: this.estimateDataRate(distKm),
          elevationDeg: 45.0 * durationFactor,
          phaseAngle
        });
      }
      return windows;
    }
  };

  const QKD = {
    bb84(numQubits, channelError) {
      numQubits = numQubits || 1000;
      channelError = channelError || 0.0;
      const aliceBits = [], aliceBases = [], bobBases = [], bobMeasurements = [];
      for (let i = 0; i < numQubits; i++) {
        const ab = Math.random() < 0.5 ? 0 : 1;
        aliceBits.push(ab);
        aliceBases.push(Math.random() < 0.5 ? 'R' : 'D');
        bobBases.push(Math.random() < 0.5 ? 'R' : 'D');
      }
      for (let i = 0; i < numQubits; i++) {
        let result;
        if (bobBases[i] === aliceBases[i]) {
          result = aliceBits[i];
          if (Math.random() < channelError) result = 1 - result;
        } else {
          result = Math.random() < 0.5 ? 0 : 1;
        }
        bobMeasurements.push(result);
      }
      const aliceKey = [], bobKey = [];
      for (let i = 0; i < numQubits; i++) {
        if (aliceBases[i] === bobBases[i]) {
          aliceKey.push(aliceBits[i]);
          bobKey.push(bobMeasurements[i]);
        }
      }
      const siftedLength = aliceKey.length;
      let errors = 0;
      for (let i = 0; i < siftedLength; i++) { if (aliceKey[i] !== bobKey[i]) errors++; }
      const qber = siftedLength > 0 ? errors / siftedLength : 1.0;
      const secure = qber < 0.11;
      return {
        protocol: 'BB84',
        rawQubits: numQubits,
        siftedKeyLength: siftedLength,
        qber,
        secure,
        efficiency: siftedLength / numQubits,
        aliceKeyPreview: aliceKey.slice(0, 40),
        bobKeyPreview: bobKey.slice(0, 40),
        errors,
        threshold: 0.11,
        status: secure ? 'SECURE' : 'EAVESDROPPER DETECTED'
      };
    },

    e91(numPairs, channelError) {
      numPairs = numPairs || 1000;
      channelError = channelError || 0.0;
      const aliceBits = [], bobBits = [], aliceBases = [], bobBases = [];
      for (let i = 0; i < numPairs; i++) {
        const bit = Math.random() < 0.5 ? 0 : 1;
        aliceBits.push(bit);
        let bBit = bit;
        if (Math.random() < channelError) bBit = 1 - bBit;
        bobBits.push(bBit);
        aliceBases.push(Math.random() < 0.5 ? 'R' : 'D');
        bobBases.push(Math.random() < 0.5 ? 'R' : 'D');
      }
      const aliceKey = [], bobKey = [];
      for (let i = 0; i < numPairs; i++) {
        if (aliceBases[i] === bobBases[i]) {
          aliceKey.push(aliceBits[i]);
          bobKey.push(bobBits[i]);
        }
      }
      const siftedLength = aliceKey.length;
      let errors = 0;
      for (let i = 0; i < siftedLength; i++) { if (aliceKey[i] !== bobKey[i]) errors++; }
      const qber = siftedLength > 0 ? errors / siftedLength : 1.0;
      const secure = qber < 0.11;
      return {
        protocol: 'E91',
        rawPairs: numPairs,
        siftedKeyLength: siftedLength,
        qber,
        secure,
        efficiency: siftedLength / numPairs,
        aliceKeyPreview: aliceKey.slice(0, 40),
        bobKeyPreview: bobKey.slice(0, 40),
        errors,
        threshold: 0.11,
        bellViolation: secure ? (2.0 + Math.random() * 0.828).toFixed(3) : 'N/A',
        status: secure ? 'SECURE' : 'EAVESDROPPER DETECTED'
      };
    },

    keyRate(distanceKm) {
      const baseRate = 10000;
      const attenuation = 0.0001;
      let rate;
      if (distanceKm < 1000) {
        rate = baseRate * Math.exp(-attenuation * distanceKm);
      } else if (distanceKm < 40000) {
        rate = baseRate * Math.exp(-attenuation * distanceKm) / 10;
      } else {
        rate = baseRate * Math.exp(-attenuation * 40000) / 100;
      }
      return Math.max(1, rate);
    }
  };

  const Routing = {
    selectAction(state) {
      if (!state.neighbors || state.neighbors.length === 0) {
        return { action: 'STORE', nextHop: null, confidence: 1.0, reasoning: 'No neighbors available, storing locally' };
      }
      if (state.neighbors.includes(state.destination)) {
        const q = state.linkQualities[state.destination] || 0;
        if (q >= 0.3) {
          return { action: 'FORWARD', nextHop: state.destination, confidence: 0.95, reasoning: 'Destination reachable directly (q=' + q.toFixed(2) + ')' };
        }
      }
      if (Math.random() < 0.1) {
        return this._explore(state);
      }
      return this._exploit(state);
    },

    _explore(state) {
      const valid = state.neighbors.filter(n => (state.linkQualities[n] || 0) >= 0.3);
      if (valid.length > 0) {
        const hop = valid[Math.floor(Math.random() * valid.length)];
        return { action: 'FORWARD', nextHop: hop, confidence: 0.3, reasoning: 'Exploration: random forward to ' + hop };
      }
      return { action: 'STORE', nextHop: null, confidence: 0.3, reasoning: 'No valid neighbors for exploration' };
    },

    _exploit(state) {
      if (state.bundlePriority <= 1) return this._findFastest(state);
      if (state.bufferOccupancy > 0.8 && state.bundlePriority >= 3) {
        return { action: 'DROP', nextHop: null, confidence: 0.7, reasoning: 'High buffer, dropping low-priority bundle' };
      }
      return this._findBest(state);
    },

    _findFastest(state) {
      const sorted = state.neighbors
        .map(n => ({ name: n, quality: state.linkQualities[n] || 0 }))
        .filter(n => n.quality >= 0.3)
        .sort((a, b) => b.quality - a.quality);
      if (sorted.length > 0) {
        return { action: 'FORWARD', nextHop: sorted[0].name, confidence: 0.8, reasoning: 'Urgent: best link to ' + sorted[0].name + ' (q=' + sorted[0].quality.toFixed(2) + ')' };
      }
      return { action: 'STORE', nextHop: null, confidence: 0.6, reasoning: 'No acceptable links, storing urgent bundle' };
    },

    _findBest(state) {
      const scored = {};
      for (const n of state.neighbors) {
        const q = state.linkQualities[n] || 0;
        if (q < 0.3) continue;
        let score = q * 0.7;
        if (state.destination.includes('earth') && n.includes('earth')) score += 0.2;
        else if (state.destination.includes('mars') && n.includes('mars')) score += 0.2;
        else if (n.includes('transit')) score += 0.1;
        scored[n] = score;
      }
      const best = Object.entries(scored).sort((a, b) => b[1] - a[1]);
      if (best.length > 0) {
        return { action: 'FORWARD', nextHop: best[0][0], confidence: 0.75, reasoning: 'Best score for ' + best[0][0] + ' (score=' + best[0][1].toFixed(2) + ')' };
      }
      return { action: 'STORE', nextHop: null, confidence: 0.5, reasoning: 'No acceptable neighbors' };
    },

    calculateReward(delivered, delaySec, hops, dropped, energyWh) {
      let r = 0;
      if (delivered) r += 1.0;
      r -= 0.001 * delaySec;
      r -= 0.1 * hops;
      if (dropped) r -= 10.0;
      r -= 0.01 * (energyWh || 0);
      return r;
    },

    simulateRoute(route, bundle) {
      const steps = [];
      let totalDelay = 0;
      let totalHops = 0;
      let delivered = false;
      let dropped = false;

      for (let i = 0; i < route.length; i++) {
        const node = route[i];
        const neighbors = i < route.length - 1
          ? route.slice(Math.max(0, i - 1), i + 2).filter(n => n !== node)
          : [];
        const linkQualities = {};
        neighbors.forEach(n => { linkQualities[n] = 0.5 + Math.random() * 0.5; });

        const state = {
          currentNode: node,
          neighbors,
          linkQualities,
          bufferOccupancy: Math.random() * 0.8,
          bundlePriority: bundle.priority,
          bundleSizeMb: bundle.sizeMb,
          bundleDeadlineHours: bundle.deadlineHours,
          destination: route[route.length - 1]
        };

        const decision = this.selectAction(state);
        const delay = 120 + Math.random() * 600;
        totalDelay += delay;
        totalHops++;

        if (decision.action === 'DROP') { dropped = true; break; }
        if (decision.action === 'STORE') { totalDelay += 300; }

        steps.push({
          step: i + 1,
          node,
          action: decision.action,
          nextHop: decision.nextHop,
          confidence: decision.confidence,
          reasoning: decision.reasoning,
          delaySec: delay,
          linkQuality: decision.nextHop ? (linkQualities[decision.nextHop] || 0) : null
        });

        if (node === route[route.length - 1]) { delivered = true; break; }
      }

      const reward = this.calculateReward(delivered, totalDelay, totalHops, dropped, totalHops * 0.5);
      return { steps, totalDelay, totalHops, delivered, dropped, reward, bundleId: bundle.id };
    }
  };

  const Bundle = {
    _id: 0,
    create(params) {
      const id = 'BND-' + (++this._id).toString(16).toUpperCase().padStart(4, '0');
      return {
        id,
        source: params.source || 'mars.surface.rover-01',
        destination: params.destination || 'earth.control.moc',
        priority: params.priority || 2,
        priorityName: ['EMERGENCY', 'HIGH_SCIENCE', 'STANDARD', 'HOUSEKEEPING', 'BULK'][params.priority || 2],
        sizeMb: params.sizeMb || 100,
        deadlineHours: params.deadlineHours || 168,
        lifetimeDays: params.lifetimeDays || 7,
        createdAt: Date.now(),
        hops: [],
        custodyHolders: [],
        status: 'CREATED'
      };
    },

    addHop(bundle, nodeId, action) {
      bundle.hops.push({ node: nodeId, action, timestamp: Date.now(), hopNumber: bundle.hops.length + 1 });
      return bundle;
    }
  };

  const Mission = {
    runScenario(config) {
      const startDay = config.startDay || 0;
      const durationDays = config.durationDays || 30;
      const windows = Orbital.contactWindows(startDay, durationDays);
      const avgDistance = windows.reduce((s, w) => s + w.distanceKm, 0) / (windows.length || 1);
      const linkResult = LinkBudget.calculate({ distanceKm: avgDistance, ...config.linkParams });

      const totalDataGB = windows.reduce((s, w) => s + (w.maxDataRateMbps * w.durationHours * 3600 / 8 / 1024), 0);
      const bundles = [];
      const dataTypes = [
        { name: 'Emergency Telemetry', priority: 0, sizeMb: 10, count: config.bundleCount || 20 },
        { name: 'Science Data', priority: 1, sizeMb: 500, count: config.bundleCount || 50 },
        { name: 'Navigation Updates', priority: 1, sizeMb: 5, count: config.bundleCount || 30 },
        { name: 'Housekeeping', priority: 3, sizeMb: 50, count: config.bundleCount || 40 },
        { name: 'Software Patches', priority: 4, sizeMb: 200, count: config.bundleCount || 5 }
      ];
      let totalBundles = 0;
      let totalVolumeMb = 0;
      for (const dt of dataTypes) {
        const vol = dt.sizeMb * dt.count;
        totalBundles += dt.count;
        totalVolumeMb += vol;
        bundles.push({ ...dt, volumeMb: vol });
      }

      const route = config.route || ['mars.surface.rover-01', 'mars.areo.alpha', 'transit.esl4.relay', 'earth.leo.constellation', 'earth.dsn.goldstone', 'earth.control.moc'];
      const simResult = Routing.simulateRoute(route, { priority: 2, sizeMb: 500, deadlineHours: 168 });

      const bb84Clean = QKD.bb84(1000, 0.0);
      const bb84Eve = QKD.bb84(1000, 0.25);

      return {
        scenarioName: config.name || 'Mars Mission Scenario',
        startDay,
        durationDays,
        contactWindows: windows,
        totalContactHours: windows.reduce((s, w) => s + w.durationHours, 0),
        avgDistanceMKm: avgDistance / 1e6,
        linkBudget: linkResult,
        totalDataTransferGB: totalDataGB,
        bundles,
        totalBundles,
        totalVolumeMb,
        routingSimulation: simResult,
        qkdClean: bb84Clean,
        qkdEavesdropped: bb84Eve,
        timeline: Orbital.distanceTimeline(durationDays)
      };
    }
  };

  const RFBudget = {
    BANDS: {
      'Ka-band': 26.5e9,
      'X-band': 8.4e9,
      'S-band': 2.3e9,
      'UHF': 401e6
    },
    SPEED_OF_LIGHT: 299792458,
    BOLTZMANN: 1.380649e-23,

    calculate(d) {
      const freq = d.frequency_hz;
      const dist_m = d.distance_km * 1000;
      const fspl = 20 * Math.log10(4 * Math.PI * dist_m * freq / this.SPEED_OF_LIGHT);
      const txGain = 10 * Math.log10(0.55 * Math.pow(Math.PI * d.tx_diameter_m * freq / this.SPEED_OF_LIGHT, 2));
      const rxGain = 10 * Math.log10(0.55 * Math.pow(Math.PI * d.rx_diameter_m * freq / this.SPEED_OF_LIGHT, 2));
      const txPowerDbm = 10 * Math.log10(d.tx_power_watts * 1000);
      const eirp = txPowerDbm + txGain - 1.0;
      const rxPower = eirp - fspl - 1.0 + rxGain - 0.5 - 0.5 - 2.0;
      const tSys = 50 + 290 * (Math.pow(10, 2.0/10) - 1);
      const noiseDbm = 10 * Math.log10(this.BOLTZMANN * tSys * d.bandwidth_hz * 1000);
      const cnr = rxPower - noiseDbm;
      const ebN0 = cnr - 10 * Math.log10(d.data_rate_bps);
      const margin = ebN0 - 10.0;
      return { frequency_hz: freq, fspl_db: fspl, tx_gain_dbi: txGain, rx_gain_dbi: rxGain,
               eirp_dbm: eirp, rx_power_dbm: rxPower, noise_power_dbm: noiseDbm,
               cnr_db: cnr, eb_n0_db: ebN0, margin_db: margin, tSys_k: tSys };
    }
  };

  const LTP = {
    segment(payload, mtu) {
      const segments = [];
      const bytes = typeof payload === 'string' ? new TextEncoder().encode(payload) : payload;
      for (let i = 0; i < bytes.length; i += mtu) {
        segments.push({
          sessionId: 'ses-' + Math.random().toString(36).substr(2,6),
          offset: i,
          isCheckpoint: i === 0,
          isEORS: (i + mtu) >= bytes.length,
          size: Math.min(mtu, bytes.length - i)
        });
      }
      return segments;
    },
    simulateTransfer(totalBytes, mtu, lossRate) {
      const segs = this.segment('x'.repeat(totalBytes), mtu);
      let sent = 0, lost = 0, retrans = 0;
      for (const s of segs) {
        sent++;
        if (Math.random() < (lossRate || 0)) { lost++; retrans++; sent++; }
      }
      return { segments: segs.length, sent, lost, retransmitted: retrans,
               efficiency: ((segs.length) / sent * 100).toFixed(1) };
    }
  };

  const Topology = {
    TIERS: [
      { name: 'Earth Ground', nodes: 5, color: '#4fc3f7' },
      { name: 'Earth Orbital', nodes: 51, color: '#29b6f6' },
      { name: 'Deep Space Transit', nodes: 4, color: '#ce93d8' },
      { name: 'Mars Orbital', nodes: 4, color: '#ef5350' },
      { name: 'Mars Surface', nodes: 177, color: '#e57373' }
    ],
    TOTAL_NODES: 241,
    LINKS: [
      { from: 0, to: 1, rate: '10 Mbps RF', latency: '10 ms' },
      { from: 1, to: 2, rate: '100 Mbps Optical', latency: '1 s' },
      { from: 2, to: 3, rate: '50 Mbps Optical', latency: '10 min' },
      { from: 3, to: 4, rate: '2 Mbps RF', latency: '1 ms' }
    ],
    getSummary() {
      return { totalNodes: this.TOTAL_NODES, tiers: this.TIERS.length, interTierLinks: this.LINKS.length };
    }
  };

  const Training = {
    train(config) {
      const rewards = [];
      let epsilon = config.epsilonStart || 1.0;
      const decay = config.decay || 0.995;
      const end = config.epsilonEnd || 0.01;
      for (let i = 0; i < config.episodes; i++) {
        const r = -2 + (1 - epsilon) * 3 + (Math.random() - 0.5) * epsilon * 4;
        rewards.push(r);
        epsilon = Math.max(end, epsilon * decay);
      }
      const avg100 = rewards.slice(-100).reduce((a,b) => a+b, 0) / Math.min(100, rewards.length);
      return { rewards, epsilonHistory: rewards.map((_, i) => Math.max(end, Math.pow(decay, i))),
               avgRewardLast100: avg100, episodes: config.episodes,
               convergence: rewards.findIndex((_, i, a) => {
                 if (i < 50) return false;
                 const s = a.slice(i-50, i);
                 const m = s.reduce((a,b)=>a+b,0)/50;
                 return s.every(v => Math.abs(v - m) < 0.5);
               }) };
    }
  };

  const Simulation = {
    run(config) {
      const steps = Math.floor(config.duration_hours * 3600 / (config.step_seconds || 3600));
      let total=0, delivered=0, dropped=0, stored=0;
      const delays = [];
      for (let t = 0; t < steps; t++) {
        if (Math.random() < (config.bundle_rate || 10) / 3600 * (config.step_seconds || 3600)) {
          total++;
          const priority = [0,0,1,1,2,2,2,3,3,4][Math.floor(Math.random()*10)];
          const hops = 3 + Math.floor(Math.random() * 4);
          const delayPerHop = 300 + Math.random() * 1200;
          const totalDelay = hops * delayPerHop;
          const deliverable = priority <= 2 || Math.random() > 0.3;
          if (deliverable) { delivered++; delays.push(totalDelay); }
          else if (Math.random() < 0.2) dropped++;
          else stored++;
        }
      }
      const avgDelay = delays.length ? delays.reduce((a,b)=>a+b,0)/delays.length : 0;
      return { total, delivered, dropped, stored, deliveryRatio: total ? delivered/total : 0,
               avgDelaySeconds: avgDelay, avgDelayMinutes: avgDelay/60,
               avgHops: delivered ? 3 + Math.random()*2 : 0, steps };
    }
  };

  const Policy = {
    POLICIES: [
      { id: 'POL-001', name: 'Emergency Fast Path', condition: 'priority <= 1', action: 'forward', target: 'best link' },
      { id: 'POL-002', name: 'Congestion Control', condition: 'buffer > 90% AND priority >= 3', action: 'drop', target: 'low priority' },
      { id: 'POL-003', name: 'Deep Space Store', condition: 'link_quality < 30%', action: 'store', target: 'local buffer' },
      { id: 'POL-004', name: 'Bulk Defer', condition: 'priority == 4 AND buffer > 50%', action: 'store', target: 'deferred queue' },
      { id: 'POL-005', name: 'Tier-Aware Routing', condition: 'dest_tier < current_tier', action: 'forward', target: 'lower-tier neighbor' }
    ],
    evaluate(ctx) {
      for (const p of this.POLICIES) {
        if (this._match(p, ctx)) return { matched: p, action: p.action, target: p.target };
      }
      return { matched: null, action: 'store', target: 'default' };
    },
    _match(policy, ctx) {
      if (policy.id === 'POL-001') return ctx.priority <= 1;
      if (policy.id === 'POL-002') return ctx.buffer > 90 && ctx.priority >= 3;
      if (policy.id === 'POL-003') return ctx.linkQuality < 0.3;
      if (policy.id === 'POL-004') return ctx.priority === 4 && ctx.buffer > 50;
      if (policy.id === 'POL-005') return ctx.destTier < ctx.currentTier;
      return false;
    }
  };

  return {
    LinkBudget,
    Orbital,
    QKD,
    Routing,
    Bundle,
    Mission,
    RFBudget,
    LTP,
    Topology,
    Training,
    Simulation,
    Policy,
    CONSTANTS: { SPEED_OF_LIGHT, SPEED_OF_LIGHT_KMS, AU_KM, DEFAULT_WAVELENGTH, EARTH_PERIOD, MARS_PERIOD, SYNODIC_PERIOD }
  };
})();
