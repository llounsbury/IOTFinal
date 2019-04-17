import {Component, HostListener, OnInit} from '@angular/core';
import { NgModule } from '@angular/core';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import * as firebase from 'firebase';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})


export class AppComponent   implements OnInit {
  public static people: any;
  title = 'iot-fe';
  public selfColumns = 1;
  public people: any;
  private orderedPeople = [];


  ngOnInit() {
    this.selfColumns = Math.floor(document.body.clientWidth / 325);
    this.getData();
  }

  getData() {
    const config = {
      apiKey: 'XXXX',
      authDomain: 'XXXX',
      databaseURL: 'XXXX',
      projectId: 'XXXX',
      storageBucket: 'XXXX',
      messagingSenderId: 'XXXX'
    };
    firebase.initializeApp(config);
    const storage = firebase.storage();
    firebase.database().ref('/people').limitToLast(100).once('value').then(snapshot => {
      this.people = snapshot.val();
      for (let [key, value] of Object.entries(this.people)) {
        this.people[key].visar = [];
        this.people[key].selected = 0;
        let temp = value;
        temp['id'] = key;
        this.orderedPeople.push(temp);
        for (let [key2, value2] of Object.entries(this.people[key].visits)) {
          const name = key2 + '.jpg';
          storage.ref().child(name).getDownloadURL().then(url => {
            const sub = 'url';
            this.people[key].visits[key2][sub] = url;
            this.people[key].visar.push(this.people[key].visits[key2]);
            this.people[key].max_slide = this.people[key].visar.length - 1;
          });
        }
      }
      this.orderedPeople = (this.orderedPeople).sort(this.compare);
    });
  }

  @HostListener('window:resize', ['$event'])
  onResize(event) {
    const width = event.target.innerWidth;
    this.selfColumns = Math.floor(width / 325);
  }

  objectKeys(input) {
    return Object.keys(input);
  }

  objectLen(input) {
    return Object.keys(input).length;
  }

  updateImage(person, input) {
    this.people[person].selected = input;
  }

  compare(a, b) {
    const sa = Object.keys(a.visits).length;
    const sb = Object.keys(b.visits).length;
    let comparison = 0;
    if (sa < sb) {
      comparison = 1;
    } else if (sb < sa) {
      comparison = -1;
    }
    return comparison;
  }
}


