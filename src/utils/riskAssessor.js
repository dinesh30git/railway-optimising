/**
 * Predictive risk assessment.
 * Assumes CSV represents a conflict-free current state.
 */
export function assessRisks(trains) {
  const risks = [];

  /* ============================
     1. OPPOSING APPROACH RISK
     ============================ */
  trains.forEach(t1 => {
    trains.forEach(t2 => {
      if (
        t1.train_id !== t2.train_id &&
        t1.direction === "UP" &&
        t2.direction === "DOWN" &&
        t1.next_block &&
        t1.next_block === t2.next_block
      ) {
        risks.push({
          message: `Opposing trains ${t1.train_id} and ${t2.train_id} approaching block ${t1.next_block}`
        });
      }
    });
  });

  /* ============================
     2. CATCH-UP RISK (Same line)
     ============================ */
  const byLine = {};

  trains.forEach(t => {
    const key = `${t.line_type}_${t.direction}`;
    if (!byLine[key]) byLine[key] = [];
    byLine[key].push(t);
  });

  Object.values(byLine).forEach(list => {
    for (let i = 0; i < list.length; i++) {
      for (let j = i + 1; j < list.length; j++) {
        const a = list[i];
        const b = list[j];

        if (
          Number(a.priority) < Number(b.priority)
        ) {
          risks.push({
            message: `Train ${a.train_id} may be delayed due to slower train ${b.train_id} ahead`
          });
        }
      }
    }
  });

  /* ============================
     3. PRIORITY CONVERGENCE RISK
     ============================ */
  trains.forEach(t => {
    if (Number(t.priority) === 1) {
      const approaching = trains.filter(
        x =>
          x.train_id !== t.train_id &&
          x.next_block === t.current_block
      );

      if (approaching.length > 0) {
        risks.push({
          message: `High-priority train ${t.train_id} approaching occupied section`
        });
      }
    }
  });

  return risks;
}
