import {Component, HostListener, OnInit} from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import {MatButtonModule, MatCardModule, MatGridListModule, MatSliderModule, MatToolbarModule, MatDialogModule, MatInputModule, MatTabsModule, MatListModule} from '@angular/material';
import { SetNameComponent } from './set-name/set-name.component';
import { FormsModule } from '@angular/forms';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { PersonInfoComponent } from './person-info/person-info.component';
import { HttpClientModule } from '@angular/common/http';

export interface Person {
  name: string;
  last_seen: number;
  id: string;
}

@NgModule({
  declarations: [
    AppComponent,
    SetNameComponent,
    PersonInfoComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    MatCardModule,
    MatButtonModule,
    MatGridListModule,
    MatSliderModule,
    MatToolbarModule,
    MatDialogModule,
    MatInputModule,
    FormsModule,
    BrowserAnimationsModule,
    HttpClientModule,
    MatTabsModule,
    MatListModule
  ],
  providers: [],
  bootstrap: [AppComponent],
  entryComponents: [SetNameComponent, PersonInfoComponent]
})
export class AppModule {}

