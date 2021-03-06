#!/usr/bin/env python
"""Test the server load view interface."""
from __future__ import division

import unittest
from grr_response_core.lib import flags

from grr_response_core.lib import rdfvalue
from grr_response_core.lib import stats
from grr_response_server import aff4
from grr_response_server.aff4_objects import stats_store
from grr_response_server.gui import gui_test_lib
from grr.test_lib import db_test_lib
from grr.test_lib import test_lib


@db_test_lib.DualDBTest
class TestServerLoadView(gui_test_lib.GRRSeleniumTest):
  """Tests for ServerLoadView."""

  @staticmethod
  def SetupSampleMetrics(token=None):
    store = aff4.FACTORY.Create(
        None, stats_store.StatsStore, mode="w", token=token)

    stats.STATS.RegisterCounterMetric("grr_frontendserver_handle_num")

    now = rdfvalue.RDFDatetime.Now()
    handle_data = [(3, now - rdfvalue.Duration("50m")),
                   (0, now - rdfvalue.Duration("45m")),
                   (1, now - rdfvalue.Duration("40m")),
                   (0, now - rdfvalue.Duration("35m")),
                   (0, now - rdfvalue.Duration("30m")),
                   (1, now - rdfvalue.Duration("25m")),
                   (0, now - rdfvalue.Duration("20m")),
                   (0, now - rdfvalue.Duration("15m")),
                   (0, now - rdfvalue.Duration("10m")),
                   (5, now - rdfvalue.Duration("5m")),
                   (0, now)]  # pyformat: disable

    handle_data = [(value, timestamp.AsMicrosecondsSinceEpoch())
                   for value, timestamp in handle_data]
    for value, timestamp in handle_data:
      with test_lib.FakeTime(timestamp / 1e6):
        stats.STATS.IncrementCounter("grr_frontendserver_handle_num", value)
        store.WriteStats(process_id="frontend")

  def testServerLoadPageContainsIndicatorsAndGraphs(self):
    self.Open("/#main=ServerLoadView")
    self.WaitUntil(self.IsTextPresent, "Frontends load")

    self.Click("css=li[heading=Worker]")
    self.WaitUntil(self.IsTextPresent, "Worker successful vs failed flows rate")

  # TODO(user): uncomment as soon as number of instances is back.
  # def testServerLoadPageShowsCorrectNumberOfInstances(self):
  #   self.SetupSampleMetrics(token=self.token)

  #   self.Open("/#main=ServerLoadView")
  #   self.WaitUntil(self.IsTextPresent, "Frontend (1 instances)")

  def testTimeRangeButtonsAreClickable(self):
    self.Open("/#main=ServerLoadView")
    self.WaitUntil(self.IsTextPresent, "Frontends load")

    self.Click("css=label[uib-btn-radio=72]")
    self.WaitUntil(self.IsTextPresent, "Frontends load")


def main(argv):
  del argv  # Unused.
  # Run the full test suite
  unittest.main()


if __name__ == "__main__":
  flags.StartMain(main)
