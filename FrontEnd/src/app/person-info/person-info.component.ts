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
  api_data: any;

  constructor(
      private http: HttpClient,
      public dialogRef: MatDialogRef<PersonInfoComponent>,
      @Inject(MAT_DIALOG_DATA) public data) {}

  ngOnInit() {
    const my_url = 'http://localhost:5000/' + this.data.id;
    console.log(my_url);
    this.api_data = this.http.get(my_url).subscribe( res => {
          console.log(res);
        }
    );
    setTimeout(() => {
      this.generateChart();
    }, 500);
  }

  onNoClick(): void {
    this.dialogRef.close();
  }

  generateChart() {
    console.log(this.data);
    const color = ['rgba(153,255,51,0.4)', 'rgba(255,153,0,0.4)', 'rgb(140, 255, 251)'];
    const chartDataSets = [];
    const cameraDataSet = {
      data: [{x: 0, y: 0}, {x: 1, y: 0}, {x: 2, y: 0}, {x: 3, y: 0}, {x: 4, y: 0}, {x: 5, y: 0}, {x: 6, y: 0}],
      label: 0,
    };
    chartDataSets[0] = chartDataSets[0] = JSON.parse(JSON.stringify(cameraDataSet));
    chartDataSets[0].label = 'Camera 1';
    chartDataSets[0].backgroundColor = color[0];

    this.data.visar.forEach( visit => {
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
    console.log(chartDataSets);
    const ctxH = document.getElementById('myChart');
    const chartJSONH = {
      type: 'line',
      data: {
        labels: ['Sun', 'Mon', 'Tues', 'Weds', 'Thurs', 'Fri', 'Sat', ],
        datasets: chartDataSets
      } };
    this.chart = new Chart(ctxH, chartJSONH);
  }

}
