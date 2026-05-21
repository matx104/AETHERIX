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

  return {
    LinkBudget,
    Orbital,
    QKD,
    Routing,
    Bundle,
    Mission,
    CONSTANTS: { SPEED_OF_LIGHT, SPEED_OF_LIGHT_KMS, AU_KM, DEFAULT_WAVELENGTH, EARTH_PERIOD, MARS_PERIOD, SYNODIC_PERIOD }
  };
})();
