import { Component, OnInit, Inject } from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material';
import * as Chart from 'chart.js';
import { HttpClient } from '@angular/common/http';



@Component({
  selector: 'app-person-info',
  templateUrl: './person-info.component.html',
  styleUrls: ['./person-info.component.css']
})
export class PersonInfoComponent implements OnInit {
  chart: Chart;
  chart2: Chart;
  api_data: any;
  corr_users: any;
  load_page = false;
  showChart2 = false;

  constructor(
      private http: HttpClient,
      public dialogRef: MatDialogRef<PersonInfoComponent>,
      @Inject(MAT_DIALOG_DATA) public data) {}

  ngOnInit() {
    const my_url = 'http://localhost:5000/' + this.data.id;
    this.api_data = this.http.get(my_url).subscribe( res => {
          console.log(res);
          this.api_data = res;
          this.api_data.correlated_users.forEach( correlation => {
            Object.keys(correlation).forEach( instance => {
              correlation['name'] = this.data.people[instance].name;
              correlation['url'] = this.data.people[instance].url;
              correlation['score'] = correlation[instance].substring(0, 4);
            });
            console.log(this.api_data.correlated_users);
          });
    }
    );
    setTimeout(() => {
      this.generateChart();
    }, 700);
  }

  onNoClick(): void {
    this.dialogRef.close();
  }

  generateChart() {
    console.log(this.data.person);
    const color = ['rgba(153,255,51,0.4)', 'rgba(255,153,0,0.4)', 'rgb(140, 255, 251)'];
    const chartDataSets = [];
    const cameraDataSet = {
      data: [{x: 0, y: 0}, {x: 1, y: 0}, {x: 2, y: 0}, {x: 3, y: 0}, {x: 4, y: 0}, {x: 5, y: 0}, {x: 6, y: 0}],
      label: 0,
    };
    chartDataSets[0] = chartDataSets[0] = JSON.parse(JSON.stringify(cameraDataSet));
    chartDataSets[0].label = 'Camera 1';
    chartDataSets[0].backgroundColor = color[0];

    this.data.person.visar.forEach( visit => {
      const day = new Date(visit.timestamp + ' UTC').getDay();
      if (!chartDataSets[visit.camera - 1]) {
        chartDataSets[visit.camera - 1] = JSON.parse(JSON.stringify(cameraDataSet));
        chartDataSets[visit.camera - 1].label = 'Camera ' + visit.camera;
        chartDataSets[visit.camera - 1].backgroundColor = color[visit.camera - 1];

      }
      chartDataSets[visit.camera - 1].data.forEach( weekDay => {
        if (weekDay.x === day) {
          weekDay.y += 1;
        }
      });
    });
    const ctxH = document.getElementById('myChart');
    const chartJSONH = {
      type: 'line',
      data: {
        labels: ['Sun', 'Mon', 'Tues', 'Weds', 'Thurs', 'Fri', 'Sat', ],
        datasets: chartDataSets
      } };
    this.chart = new Chart(ctxH, chartJSONH);
  }

  startChart2(event) {
    if (!this.showChart2 && event.index === 1) {
      setTimeout(() => {
        this.generateChart2();
      }, 50);
      this.showChart2 = true;
    }
  }

  generateChart2() {
    const color = ['rgba(153,255,51,0.4)'];
    const chartDataSets = [];
    const cameraDataSet = {
      data: [{x: 0, y: 0}, {x: 1, y: 0}, {x: 2, y: 0}, {x: 3, y: 0}, {x: 4, y: 0}, {x: 5, y: 0}, {x: 6, y: 0}],
      label: 0,
    };
    chartDataSets[0] = chartDataSets[0] = JSON.parse(JSON.stringify(cameraDataSet));
    chartDataSets[0].label = 'Total Minutes Per Weekday';
    chartDataSets[0].backgroundColor = color[0];

    this.api_data.visits.forEach( visit => {
      const start = new Date(visit.start + ' UTC');
      const end =  new Date(visit.end + ' UTC');
      const day = start.getDay();
      // @ts-ignore
      let diffMin = (end - start) * 0.00001666667;
      if (diffMin < 5) {
        diffMin = 5;
      }
      chartDataSets[0].data.forEach( weekDay => {
        if (weekDay.x === day) {
          weekDay.y += diffMin;
        }
      });
    });
    const ctxH = document.getElementById('myChart2');
    const chartJSONH = {
      type: 'line',
      data: {
        labels: ['Sun', 'Mon', 'Tues', 'Weds', 'Thurs', 'Fri', 'Sat', ],
        datasets: chartDataSets
      } };
    this.chart = new Chart(ctxH, chartJSONH);
  }

}
